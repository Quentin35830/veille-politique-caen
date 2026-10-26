"""Veille politique quotidienne Caen & Caen la Mer, envoyee par Gmail."""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any

import mistralai.workflows as workflows
from mistralai.workflows import Depends
from mistralai.workflows.client import get_mistral_client
from mistralai.workflows.plugins.mistralai.connectors import (
    ToolCallClient,
    connector,
    uses_connectors,
)

RECIPIENT = "quentin.tizon@proton.me"

gmail_connector = connector("gmail", run_as="deployment")

MONTHS_FR = {
    1: "janvier", 2: "fevrier", 3: "mars", 4: "avril", 5: "mai", 6: "juin",
    7: "juillet", 8: "aout", 9: "septembre", 10: "octobre", 11: "novembre", 12: "decembre",
}


def _today_fr() -> str:
    now = datetime.now(timezone(timedelta(hours=1)))
    return f"{now.day} {MONTHS_FR[now.month]} {now.year}"


def _as_dict(obj: Any) -> dict:
    if isinstance(obj, dict):
        return obj
    data = getattr(obj, "model_dump", None)
    if callable(data):
        try:
            return data()
        except Exception:
            pass
    if hasattr(obj, "__dict__"):
        return vars(obj)
    return {}


async def _acall(obj: Any, name: str, **kwargs: Any) -> Any:
    fn = getattr(obj, f"{name}_async", None)
    if fn is not None:
        return await fn(**kwargs)
    return await asyncio.to_thread(getattr(obj, name), **kwargs)


INSTRUCTIONS = """Tu es un agent de veille d'actualites politiques locales pour Caen et la communaute
urbaine Caen la Mer (Calvados, Normandie).

PERIMETRE : les 48 communes de Caen la Mer : Caen, Authie, Benouville, Bieville-Beuville,
Blainville-sur-Orne, Bourguebus, Bretteville-sur-Odon, Cairon, Cambes-en-Plaine, Carpiquet,
Le Castelet, Castine-en-Plaine, Colleville-Montgomery, Colombelles, Cormelles-le-Royal,
Cuverville, Demouville, Epron, Eterville, Fleury-sur-Orne, Le Fresne-Camilly, Giberville,
Grentheville, Hermanville-sur-Mer, Herouville-Saint-Clair, Ifs, Lion-sur-Mer, Louvigny, Mathieu,
Mondeville, Mouen, Ouistreham, Periers-sur-le-Dan, Rosel, Rots, Saint-Andre-sur-Orne,
Saint-Aubin-d'Arquenay, Saint-Contest, Saint-Germain-la-Blanche-Herbe, Saint-Manvieu-Norrey,
Sannerville, Soliers, Thaon, Thue et Mue, Tourville-sur-Odon, Troarn, Verson, Villons-les-Buissons.

TU CHERCHES (actualites politiques communales et intercommunales, dernieres 24 a 48 heures) :
conseils municipaux et deliberation, budgets et fiscalite locale, urbanisme et projets
d'amenagement, grands projets intercommunaux (tramway, Caen Presqu'ile, EPOPEA, pont de
Colombelles, reseau de chaleur), inaugurations, manifestations et evenements publics, tribunes et
declarations d'elus ou de l'opposition, alertes et mobilisations citoyennes, consultations
publiques, transports et mobilite, logement et action sociale, environnement, elections locales.
EXCLUS : politique nationale ou departementale sans impact direct sur les communes du perimetre,
et faits divers sans dimension politique.

METHODE : effectue plusieurs recherches web ciblant la presse locale (Ouest-France, France 3
Normandie, Paris-Normandie, actu.fr, La Renaissance le Bocage, Liberté de Normandie) avec des
requetes comme : "Caen conseil municipal", "Caen la Mer communaute urbaine", "maire Caen",
"Caen urbanisme projet", "tramway Caen", plus des requetes ciblees sur les principales communes
(Herouville-Saint-Clair, Mondeville, Colombelles, Ifs, Fleury-sur-Orne, Ouistreham, Carpiquet,
Blainville-sur-Orne, Cormelles-le-Royal, Louvigny, Verson, Giberville...). Ne garde que les
actualites des dernieres 24 a 48 heures, deduplique.

FORMAT DE SORTIE : renvoie UNIQUEMENT le corps HTML d'un email, simple et lisible, sans les
balises <html> ni <head> : une section par theme (Vie municipale, Urbanisme & projets,
Mobilite & transports, Evenements & inaugurations, Opposition & societe civile, Autres communes
de l'aggo). Pour chaque actualite : titre en gras, 2 a 3 lignes de resume, la commune concernee
entre crochets, et un lien <a href="..."> vers la source. Si aucune actualite notable : un email
court "Rien a signaler aujourd'hui". Ecris en francais correct avec accents.
"""


@workflows.activity(start_to_close_timeout=timedelta(minutes=12))
async def collect_news() -> str:
    """Fait la veille via un agent avec recherche web et renvoie le corps HTML de l'email."""
    client = get_mistral_client()

    agent = await _acall(
        client.beta.agents,
        "create",
        name="veille-politique-caen",
        description="Agent de veille politique locale Caen & Caen la Mer",
        instructions=INSTRUCTIONS,
        tools=[{"type": "web_search"}],
        completion_args={"temperature": 0.2},
    )
    agent_dict = _as_dict(agent)
    agent_id = agent_dict.get("id") or getattr(agent, "id", None)

    inputs = (
        "Produis la synthese HTML de veille politique pour aujourd'hui "
        f"({_today_fr()}) : cherche les actualites des dernieres 24 a 48 heures "
        "et renvoie uniquement le corps HTML de l'email, pret a etre envoye."
    )

    conv = await _acall(client.beta.conversations, "start", agent_id=agent_id, inputs=inputs)
    conv_dict = _as_dict(conv)

    html_parts: list[str] = []
    for entry in conv_dict.get("outputs", []) or []:
        entry_d = _as_dict(entry)
        if entry_d.get("type") == "message.output":
            for item in entry_d.get("content", []) or []:
                item_d = _as_dict(item)
                if item_d.get("type") == "text":
                    html_parts.append(item_d.get("text", ""))
    html_body = "\n".join(html_parts).strip()

    if not html_body or "<" not in html_body:
        html_body = "<p>Rien a signaler aujourd'hui.</p>"
    return html_body


@workflows.activity(start_to_close_timeout=timedelta(minutes=5))
async def send_veille(
    subject: str,
    html_body: str,
    gmail: ToolCallClient = Depends(gmail_connector),
) -> Any:
    """Envoie la synthese par Gmail."""
    return await gmail.call_tool(
        tool_name="send_email",
        arguments={
            "to": [RECIPIENT],
            "subject": subject,
            "htmlBody": html_body,
            "_confirmationReason": "Envoi automatique de la veille politique Caen & Caen la Mer, autorise par l'utilisateur.",
        },
    )


@workflows.workflow.define(
    name="veille-politique-caen",
    workflow_display_name="Veille politique Caen & Caen la Mer",
    workflow_description="Veille politique quotidienne Caen & Caen la Mer envoyee par Gmail.",
)
@uses_connectors(gmail_connector)
class VeillePolitiqueCaenWorkflow:
    @workflows.workflow.entrypoint
    async def run(self, input: dict | None = None) -> dict:
        subject = f"Veille politique Caen & Caen la Mer - {_today_fr()}"
        html_body = await collect_news()
        result = await send_veille(subject, html_body)
        return {"subject": subject, "sent": str(result)[:2000]}
