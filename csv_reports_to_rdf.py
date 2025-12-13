
#for converting csv reports to RDF Turtle format
# csv_reports_to_rdf.py
import csv
from rdflib import Graph, Namespace, Literal, RDF, XSD, URIRef

BASE = "http://fieldlab2.org/data/"
SORD = Namespace("http://fieldlab2.org/ontology/sord#")
SCHEMA = Namespace("http://schema.org/")

def convert(csv_file, output_file):
    g = Graph()
    g.bind("sord", SORD)
    g.bind("schema", SCHEMA)

    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if not row.get("case_id"):  
                continue  # skip empty rows

            # -------------------------
            # URIs for this incident
            # -------------------------
            incident_uri = URIRef(BASE + row["case_id"])
            loc_uri      = URIRef(BASE + "location_"   + row["case_id"])
            victim_uri   = URIRef(BASE + "victim_"     + row["case_id"])
            perp_uri     = URIRef(BASE + "perp_"       + row["case_id"])
            pub_uri      = URIRef(BASE + "publication_" + row["case_id"])

            # -------------------------
            # INCIDENT
            # -------------------------
            g.add((incident_uri, RDF.type, SORD.SexualViolenceIncident))
            g.add((incident_uri, SORD.recordId, Literal(row["case_id"])))
            g.add((incident_uri, SORD.organisationId, Literal(row["org_id"])))
            g.add((incident_uri, SORD.inputBy, Literal(row["input_by"])))

            # Dates
            if row["date_received"]:
                g.add((incident_uri, SORD.dateReportReceived,
                       Literal(row["date_received"], datatype=XSD.date)))

            if row["date_recorded"]:
                g.add((incident_uri, SORD.recordedDate,
                       Literal(row["date_recorded"], datatype=XSD.date)))

            if row["incident_date"]:
                g.add((incident_uri, SORD.incidentDate,
                       Literal(row["incident_date"])))

            # Incident type + short description
            if row["violence_type"]:
                g.add((incident_uri, SORD.incidentType,
                       Literal(row["violence_type"])))

            if row["short_desc"]:
                g.add((incident_uri, SCHEMA.description,
                       Literal(row["short_desc"])))

            # Link to victim, perpetrator, location, publication
            g.add((incident_uri, SORD.hasLocation, loc_uri))
            g.add((incident_uri, SORD.hasVictim, victim_uri))
            g.add((incident_uri, SORD.hasPerpetrator, perp_uri))
            g.add((incident_uri, SORD.hasPublication, pub_uri))

            # LOCATION
            g.add((loc_uri, RDF.type, SORD.Location))

            location_label = ", ".join(filter(None, [
                row["village"],
                row["town"],
                row["state"],
                row["country"],
                row["camp"]   # camp last because it's optional
            ]))

            if location_label:
                g.add((loc_uri, SORD.locationName, Literal(location_label)))


            # -------------------------
            # VICTIM
            # -------------------------
            g.add((victim_uri, RDF.type, SORD.Victim))

            if row["num_victims"]:
                try:
                    g.add((victim_uri, SORD.numberOfVictims,
                           Literal(int(row["num_victims"]), datatype=XSD.integer)))
                except ValueError:
                    pass

            if row["victim_age"]:
                # Store age as string (handles ranges like "18-25" or "Under 18")
                g.add((victim_uri, SORD.age, Literal(row["victim_age"])))

            if row["victim_gender"]:
                g.add((victim_uri, SORD.gender, Literal(row["victim_gender"])))

            # -------------------------
            # PERPETRATOR
            # -------------------------
            g.add((perp_uri, RDF.type, SORD.Perpetrator))

            if row["num_perpetrators"]:
                g.add((perp_uri, SORD.numberOfPerpetrators,
                       Literal(int(row["num_perpetrators"]))))

            if row["perp_affiliation"]:
                g.add((perp_uri, SORD.affiliation,
                       Literal(row["perp_affiliation"])))

            # -------------------------
            # PUBLICATION
            # -------------------------
            g.add((pub_uri, RDF.type, SORD.Publication))

            if row["pub_type"]:
                g.add((pub_uri, SORD.publicationType,
                       Literal(row["pub_type"])))

            if row["pub_date"]:
                g.add((pub_uri, SCHEMA.datePublished,
                       Literal(row["pub_date"], datatype=XSD.date)))

            if row["pub_link"]:
                g.add((pub_uri, SCHEMA.url,
                       Literal(row["pub_link"])))

    # -------------------------
    # Save the RDF graph
    # -------------------------
    g.serialize(destination=output_file, format="turtle")
    print(f"✔ RDF written to {output_file}")


if __name__ == "__main__":
    convert("reports.csv", "reports_sord.ttl")
