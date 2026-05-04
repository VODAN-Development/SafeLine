import csv
from rdflib import Graph, Namespace, Literal, RDF, XSD, URIRef

BASE = "http://fieldlab2.org/data/"
SORD = Namespace("http://fieldlab2.org/ontology/sord#")
SCHEMA = Namespace("http://schema.org/")
GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")

def convert(csv_file, output_file):
    g = Graph()
    g.bind("sord", SORD)
    g.bind("schema", SCHEMA)
    g.bind("geo", GEO)

    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            incident_id = row.get("incident_id")
            if not incident_id:
                continue  # skip empty rows

            # -------------------------
            # URIs for this incident
            # -------------------------
            incident_uri = URIRef(BASE + incident_id)
            loc_uri      = URIRef(BASE + "location_"   + incident_id)
            victim_uri   = URIRef(BASE + "victim_"     + incident_id)
            perp_uri     = URIRef(BASE + "perp_"       + incident_id)
            pub_uri      = URIRef(BASE + "publication_" + incident_id)

            # -------------------------
            # INCIDENT
            # -------------------------
            g.add((incident_uri, RDF.type, SORD.SexualViolenceIncident))

            if row.get("org_id"):
                g.add((incident_uri, SORD.organisationId, Literal(row["org_id"])))
            if row.get("input_by"):
                g.add((incident_uri, SORD.inputBy, Literal(row["input_by"])))
            if row.get("date_received"):
                g.add((incident_uri, SORD.dateReportReceived, Literal(row["date_received"], datatype=XSD.date)))
            if row.get("date_recorded"):
                g.add((incident_uri, SORD.dateReportRecorded, Literal(row["date_recorded"], datatype=XSD.date)))
            
            if row.get("incident_date"):
                g.add((incident_uri, SORD.incidentDate, Literal(row["incident_date"], datatype=XSD.date)))
            
            # Map time range to schema.org temporal tracking
            if row.get("incident_time_range") and row["incident_time_range"] != "Unknown":
                g.add((incident_uri, SCHEMA.temporal, Literal(row["incident_time_range"])))
                
            if row.get("violence_type"):
                g.add((incident_uri, SORD.violenceType, Literal(row["violence_type"])))
            if row.get("short_desc"):
                g.add((incident_uri, SCHEMA.description, Literal(row["short_desc"])))

            # -------------------------
            # LOCATION
            # -------------------------
            g.add((incident_uri, SORD.hasLocation, loc_uri))
            g.add((loc_uri, RDF.type, SORD.Location))

            if row.get("country"):
                g.add((loc_uri, SORD.country, Literal(row["country"])))
            if row.get("state"):
                g.add((loc_uri, SORD.state, Literal(row["state"])))
            if row.get("town"):
                g.add((loc_uri, SORD.town, Literal(row["town"])))
            if row.get("village"):
                g.add((loc_uri, SORD.village, Literal(row["village"])))
            if row.get("camp"):
                g.add((loc_uri, SORD.camp, Literal(row["camp"])))
                
            # Standards-Aligned GEO Mapping
            if row.get("latitude") and row["latitude"] != "None":
                g.add((loc_uri, GEO.lat, Literal(row["latitude"], datatype=XSD.float)))
            if row.get("longitude") and row["longitude"] != "None":
                g.add((loc_uri, GEO.long, Literal(row["longitude"], datatype=XSD.float)))

            # -------------------------
            # VICTIM
            # -------------------------
            g.add((incident_uri, SORD.hasVictim, victim_uri))
            g.add((victim_uri, RDF.type, SORD.Victim))

            if row.get("num_victims") and row["num_victims"] != "None":
                g.add((incident_uri, SORD.numberOfVictims, Literal(int(float(row["num_victims"])))))
            if row.get("victim_age") and row["victim_age"] != "None":
                g.add((victim_uri, SORD.age, Literal(int(float(row["victim_age"])))))
            if row.get("victim_gender"):
                g.add((victim_uri, SORD.gender, Literal(row["victim_gender"])))

            # -------------------------
            # PERPETRATOR
            # -------------------------
            g.add((incident_uri, SORD.hasPerpetrator, perp_uri))
            g.add((perp_uri, RDF.type, SORD.Perpetrator))

            if row.get("num_perpetrators") and row["num_perpetrators"] != "None":
                g.add((perp_uri, SORD.numberOfPerpetrators, Literal(int(float(row["num_perpetrators"])))))
            if row.get("perp_affiliation"):
                g.add((perp_uri, SORD.affiliation, Literal(row["perp_affiliation"])))

            # -------------------------
            # PUBLICATION
            # -------------------------
            g.add((incident_uri, SORD.hasSource, pub_uri))
            g.add((pub_uri, RDF.type, SORD.Publication))

            if row.get("pub_type"):
                g.add((pub_uri, SORD.publicationType, Literal(row["pub_type"])))
            if row.get("pub_date"):
                g.add((pub_uri, SCHEMA.datePublished, Literal(row["pub_date"], datatype=XSD.date)))
            if row.get("pub_link"):
                g.add((pub_uri, SCHEMA.url, Literal(row["pub_link"])))

    # -------------------------
    # Save the RDF graph
    # -------------------------
    g.serialize(destination=output_file, format="turtle")