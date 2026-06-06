#!/usr/bin/python3
# Copyright (c) BDist Development Team
# Distributed under the terms of the Modified BSD License.
import os
from logging.config import dictConfig

from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from psycopg.rows import namedtuple_row
from psycopg_pool import ConnectionPool

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s:%(lineno)s - %(funcName)20s(): %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)

RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")

app = Flask(__name__)
app.json.ensure_ascii = False
app.json.sort_keys = False
app.config.from_prefixed_env()
log = app.logger
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=RATELIMIT_STORAGE_URI,
)

# Use the DATABASE_URL environment variable if it exists, otherwise use the default.
# Use the format postgres://username:password@hostname/database_name to connect to the database.
DATABASE_URL = os.environ.get("DATABASE_URL", "postgres://app:app@postgres/app")

pool = ConnectionPool(
    conninfo=DATABASE_URL,
    kwargs={
        "autocommit": True,  # If True don’t start transactions automatically.
        "row_factory": namedtuple_row,
    },
    min_size=4,
    max_size=10,
    open=True,
    # check=ConnectionPool.check_connection,
    name="postgres_pool",
    timeout=5,
)

try:
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT setval(pg_get_serial_sequence('venda', 'no_venda'), COALESCE(MAX(no_venda), 0) + 1, false) FROM venda;
                SELECT setval(pg_get_serial_sequence('bilhete', 'bid'), COALESCE(MAX(bid), 0) + 1, false) FROM bilhete;
            """)
    log.info("Sequências da base de dados sincronizadas com sucesso no arranque!")
except Exception as e:
    log.error(f"Erro na sincronização de sequências inicial: {e}")

def is_decimal(s):
    """Returns True if string is a parseable float number."""
    try:
        float(s)
        return True
    except ValueError:
        return False

@app.route(
    "/zona/<zona>",
    methods=("GET",))
def zona_index(zona):
    """ lista de todos os recintos da <zona>, contendo o número do recinto e as espécies nele contidas,
    indicando, para cada espécie, os nomes científico e comum, e o número de animais da espécie que estão no recinto."""

    if not is_decimal(zona):
        return jsonify({"message": "zona deve ser decimal.", "status": "error"}), 400
    
    with pool.connection() as conn:
        with conn.cursor() as cur:

            exist = cur.execute(
                "SELECT 1 FROM zona WHERE id_zona = %(zona)s;",
                {"zona": zona}
            ).fetchone()

            if not exist:
                return jsonify({"message": f"A zona com o ID {zona} não existe.", "status": "error"}), 404

            search = cur.execute(
                """
                SELECT r.id_recinto, e.nome_cientifico, e.nome_comum, COUNT(a.id_animal) as quantidade
                FROM recinto r LEFT JOIN animal a ON r.id_recinto = a.id_recinto
                               LEFT JOIN especie e ON a.nome_cientifico = e.nome_cientifico
                WHERE r.id_zona = %(zona)s
                GROUP BY r.id_recinto, e.nome_cientifico, e.nome_comum
                ORDER BY r.id_recinto ASC;
                """,
                {"zona": zona},
            ).fetchall()

            log.debug(f"Found {cur.rowcount} rows.")
            
            if not search:
                return jsonify([]), 200

            result = {}

            for line in search:
              id_rec = line[0]
              nome_cientifico = line[1]
              nome_comum = line[2]
              quant = line[3]

              if id_rec not in result:
                result[id_rec] = {
                    "número recinto": id_rec,
                    "espécies": []
                }

              if nome_cientifico is not None:
                  result[id_rec]["espécies"].append({
                      "nome": nome_comum,
                      "nome científico": nome_cientifico,
                      "quantidade": quant
                  })

            log.debug("Prepared values.")

            result = list(result.values())

    return jsonify(result), 200

@app.route(
    "/recinto/<recinto>/voto/<bilhete>/",
    methods=(
        "POST",
    ),
)
def recinto_voto_save(recinto, bilhete):
    """ Assinala o voto do <bilhete> no <recinto>, atualizando as tabelas bilhete e recinto. """
    
    if not is_decimal(bilhete):
        return jsonify({"message": "Bilhete is required to be decimal.", "status": "error"}), 400
    if not is_decimal(recinto):
        return jsonify({"message": "Recinto is required to be decimal.", "status": "error"}), 400

    with pool.connection() as conn:
        with conn.cursor() as cur:
            try:
                with conn.transaction():
                    state = cur.execute(
                        """
                        SELECT votou
                        FROM bilhete
                        WHERE bid = %(bilhete)s
                        FOR UPDATE;
                        """,
                        {"bilhete": bilhete},                
                    ).fetchone()

                    if state is None:
                        return jsonify({"message": "Bilhete não encontrado.", "status": "error"}), 404

                    if state[0] is True:
                        return jsonify({"message": "Voto já computado.", "status": "error"}), 409

                    exists = cur.execute(
                        """
                        SELECT 1
                        FROM recinto
                        WHERE id_recinto = %(recinto)s
                        """,
                        {"recinto": recinto},
                    ).fetchone()

                    if exists is None:
                        return jsonify({"message": "Recinto não encontrado.", "status": "error"}), 404
                    
                    contains = cur.execute(
                        """
                        SELECT 1
                        FROM acesso JOIN recinto USING (id_zona)
                        WHERE bid = %(bilhete)s AND id_recinto = %(recinto)s;  
                        """,
                        {"bilhete": bilhete, "recinto": recinto},
                    ).fetchone()

                    if contains is None:
                        return jsonify({"message": "Bilhete não tem acesso ao recinto.", "status": "error"}), 400

                    cur.execute(
                        """
                        UPDATE bilhete SET votou = true
                        WHERE bid = %(bilhete)s
                        """,
                        {"bilhete": bilhete},
                    )
                    
                    log.debug(f"Updated {cur.rowcount} rows.")

                    cur.execute(
                        """
                        UPDATE recinto SET votos = votos + 1
                        WHERE id_recinto = %(recinto)s
                        """,
                        {"recinto": recinto},
                    )

                    log.debug(f"Updated {cur.rowcount} rows.")

            except Exception as e:
                return jsonify({"message": str(e), "status": "error"}), 500
            
            else:
                log.debug(f"Rows changed: {cur.rowcount}")

    return "", 204

@app.route(
    "/venda/",
    methods=(
        "POST",
    ),
)
def venda_save():
    """ Executa uma venda de um ou mais bilhetes, populando as tabelas venda, bilhete e acesso. """

    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"message": "Input inválido.", "status": "error"}), 400
        
    nif = data.get("nif")

    if nif is not None:
        nif_str = str(nif)
        if len(nif_str) != 9 or not nif_str.isdigit():
            return jsonify({"message": "NIF tem de conter exatamente 9 dígitos.", "status": "error"}), 400
    
    bilhetes = data.get("bilhetes", [])

    if not bilhetes:
        return jsonify({"message": "Nenhum bilhete a comprar.", "status": "error"}), 400

    for bilhete in bilhetes:
        zonas = bilhete.get("zonas")
        
        if not zonas:
            return jsonify({"message": "Bilhete sem zonas.", "status": "error"}), 400

        desc = bilhete.get("desconto", 0.0)

        if not is_decimal(desc) or desc < 0 or desc > 100:
            return jsonify({"message": "Desconto inválido.", "status": "error"}), 400

    log.debug("Input received and validated.")
    
    with pool.connection() as conn:
        with conn.cursor() as cur:
            try:
                with conn.transaction():
                    todas_zonas = set()
                    for bilhete in bilhetes:
                        for zona_id in bilhete.get("zonas", []):
                            todas_zonas.add(zona_id)
    
                    precos_zonas = {}
                    for zona_id in todas_zonas:
                        row = cur.execute(
                            """
                            SELECT preco
                            FROM zona
                            WHERE id_zona = %(zona)s;
                            """,
                            {"zona": zona_id}
                        ).fetchone()
                        
                        if not row:
                            return jsonify({"message": f"Zona {zona_id} não existe.", "status": "error"}), 400
                            
                        precos_zonas[zona_id] = float(row[0])
                    
                    preco_total = 0.0
                    output = []

                    no_venda = cur.execute(
                        """
                        INSERT INTO venda (nif_cliente, data_hora)
                        VALUES (%(nif)s, NOW())
                        RETURNING no_venda;
                        """,
                        {"nif": nif}
                    ).fetchone()[0]
                
                    log.debug(f"Updated {cur.rowcount} rows. Venda created.")

                    for bilhete in bilhetes:
                        desc = bilhete.get("desconto", 0.0)
                                    
                        bid = cur.execute(
                                """
                                INSERT INTO bilhete (desconto, no_venda)
                                VALUES (%(desc)s, %(venda)s)
                                RETURNING bid;
                                """,
                                {"desc": desc, "venda": no_venda}
                            ).fetchone()[0]

                        log.debug(f"Updated {cur.rowcount} rows. Bilhete created.")
                    
                        zonas = bilhete.get("zonas")
                        total_base_bilhete = 0.0
                    
                        for zona in zonas:
                            cur.execute(
                                """INSERT INTO acesso (bid, id_zona) VALUES (%(bid)s, %(zona)s);""",
                                {"bid": bid, "zona": zona}
                            )

                            total_base_bilhete += precos_zonas[zona]
    
                        log.debug(f"Updated {cur.rowcount} rows. Zonas analyzed.")
                        
                        preco_com_desconto = total_base_bilhete * (1.0 - (desc / 100.0))
                        preco_total += preco_com_desconto
                        
                        output.append({
                                "id": bid,
                                "preco": round(preco_com_desconto, 2)
                            })
                
            except Exception as e:
                log.debug(f"Error: {e}")
                return jsonify({"message": str(e), "status": "error"}), 500

        res = {
            "total": round(preco_total, 2),
            "bilhetes": output
        }
            
        return jsonify(res), 201

if __name__ == "__main__":
    app.run()
