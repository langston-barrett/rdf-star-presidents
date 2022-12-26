use std::fs;

use anyhow::Result;
use clap::Parser;
use rio_api::formatter::TriplesFormatter;
use rio_api::model::{Literal, NamedNode, Subject, Term, Triple};
use rio_turtle::NTriplesFormatter;

#[derive(Debug, clap::Parser)]
pub struct Args {}

#[derive(Debug, serde::Deserialize, serde::Serialize)]
#[serde(rename_all = "camelCase")]
pub struct Query0 {
    pres: String,
    pres_label: String,
    start: String,
    end: Option<String>,
    ord: String,
    pred: Option<String>,
    succ: Option<String>,
}

fn triple<'a>(subj: &'a str, pred: &'a str, obj: &'a str) -> Triple<'a> {
    Triple {
        subject: NamedNode { iri: subj }.into(),
        predicate: NamedNode { iri: pred }.into(),
        object: NamedNode { iri: obj }.into(),
    }
}

fn meta_triple<'a>(subj: &'a Triple, pred: &'a str, obj: &'a str) -> Triple<'a> {
    Triple {
        subject: subj.into(),
        predicate: NamedNode { iri: pred }.into(),
        object: NamedNode { iri: obj }.into(),
    }
}

fn main() -> Result<()> {
    let _args = Args::parse();
    let query0_string = fs::read_to_string("raw/query0.json")?;
    let query0: Vec<Query0> = serde_json::from_str(&query0_string)?;

    let mut formatter = NTriplesFormatter::new(std::io::stdout());

    for result in query0 {
        let pres_triple = triple(
            &result.pres,
            "https://www.wikidata.org/wiki/Property:P39",
            "https://www.wikidata.org/wiki/Q11696",
        );
        formatter.format(&pres_triple)?;
        formatter.format(&Triple {
            subject: Subject::Triple(&pres_triple),
            predicate: NamedNode {
                iri: "https://www.wikidata.org/wiki/Property:P580",
            }
            .into(),
            object: Literal::Simple {
                value: &result.start[..4],
            }
            .into(),
        })?;
        formatter.format(&triple(
            &result.pres,
            "http://www.w3.org/2000/01/rdf-schema#label",
            &result.pres_label,
        ))?;
    }

    formatter.finish()?;

    Ok(())
}
