from typing import Optional, List, Callable, Dict


def _cond_ignore_line(ignore_str: Optional[str]) -> str:
    return f"    - Si el mensaje presenta alguna de estas frases/palabras (sin importar mayusculas o minusculas y considerando faltas de ortografías) {ignore_str} debes responder automaticamente WMI000: 1 y todas las demas claves con 0" if ignore_str else ""


def _cond_derive_line(derive_str: Optional[str]) -> str:
    return f"    - Si el mensaje presenta alguna de estas frases/palabras (sin importar mayusculas o minusculas y considerando faltas de ortografías) {derive_str} debes responder automaticamente WMD000: 1 y todas las demas claves con 0" if derive_str else ""


def tag_and_answer_system(categories_str: str, ignore_str: Optional[str], derive_str: Optional[str]) -> str:
    return f"""Eres un asistente encargado de clasificar mensajes de clientes (correos, tweets o tickets de soporte al cliente) en múltiples categorías. 

    ### Categorías Disponibles ###
    {categories_str}

    ### Instrucciones ###
    - Analiza el correo y determina qué categorías son relevantes.
    - Los nombres de las categorías pueden contener información entre corchetes ([]), esto es la definición de la categoría, que aporta información adicional y debes usarla para responder de forma mas precisa.
    - Responde ÚNICAMENTE con un JSON donde:
    - Las claves son los códigos de categoría (ej: WMA001).
    - Los valores son 1 si la categoría aplica, 0 si no.
{_cond_ignore_line(ignore_str)}
{_cond_derive_line(derive_str)}
    - Incluye TODAS las categorías listadas, aunque su valor sea 0.
    - No agregues comentarios, explicaciones ni formato adicional.

    Ejemplo de respuesta válida:
    {{
    "WMA001": 0,
    "WMA002": 1,
    "WMA003": 0
    }}"""


def tag_only_system(categories_str: str) -> str:
    return f"""Eres un asistente encargado de clasificar mensajes de clientes (correos, tweets o tickets de soporte al cliente) en múltiples categorías. 

    ### Categorías Disponibles ###
    {categories_str}

    ### Instrucciones ###
    - Analiza el correo y determina qué categorías son relevantes.
    - Responde ÚNICAMENTE con un JSON donde:
    - Las claves son los códigos de categoría (ej: WMA001).
    - Los valores son 1 si la categoría aplica, 0 si no.
    - Incluye TODAS las categorías listadas, aunque su valor sea 0.
    - No agregues comentarios, explicaciones ni formato adicional.

    Ejemplo de respuesta válida:
    {{
    "WMA001": 0,
    "WMA002": 1,
    "WMA003": 0
    }}"""


def tag_single_system(categories_str: str, ignore_str: Optional[str], derive_str: Optional[str]) -> str:
    return f"""Eres un asistente encargado de clasificar mensajes de clientes (correos, tweets o tickets de soporte al cliente) en una sola categoría. 

    ### Categorías Disponibles ###
    {categories_str}

    ### Instrucciones ###
    - Analiza el correo y determina la categoría relevante.
    - Los nombres de las categorías pueden contener información entre corchetes ([]), esto es la definición de la categoría, que aporta información adicional y debes usarla para responder de forma mas precisa.
    - Responde ÚNICAMENTE con un JSON donde:
    - Las claves son los códigos de categoría (ej: WMA001).
    - El valor de la categoría que corresponde debe ser 1, todas las demás deben ser 0.
{_cond_ignore_line(ignore_str)}
{_cond_derive_line(derive_str)}

    - Incluye TODAS las categorías listadas, aunque su valor sea 0.
    - No agregues comentarios, explicaciones ni formato adicional.
    
    Recuerda que SOLAMENTE UNA CATEGORÍA PUEDE TENER VALOR 1.

    Ejemplo de respuesta válida:
    {{
    "WMA001": 0,
    "WMA002": 1,
    "WMA003": 0
    }}"""


def tag_templates_system(cliente: str, aplicables: List[str], templates_str: str) -> str:
    return f"""Eres un asistente encargado de responder mensajes de clientes de la empresa {cliente}. 

            ### Instrucciones ###
            - Analiza el correo y la lista de categorías en las que se clasificó. Para cada categoría de la lista se propone un template de respuesta.
            - Debes crear un único template en base a los que se te presentan, una especie de combinacion entre ambos, siempre tratando de responder de forma correcta a lo que menciona el tweet.
            - Lo mas importante es la coherencia de la respuesta, los templates son simples y genericos y asi debe ser la respuesta. si los template NO responden de forma correcta/coherente a la problematica del cliente debes responder UNICAMENTE "Sin respuesta"
            - Prioriza la categoría que mas relación tenga con el caso, agregando elementos de los otros templates.
            - Usa máximo 2 oraciones concisas
            
            ### Lista de Categorías ###
            {aplicables}
            
            ### Templates ###
            {templates_str}
            
            """


def user_json(texto: str) -> str:
    return f"### Tweet ###\n{texto}\n\n### JSON categorias: "


def user_templates(texto: str) -> str:
    return f"### Tweet ###\n{texto}\n\n### Respuesta Template: "


prompts: Dict[str, Callable[..., str]] = {
    "tag_and_answer": tag_and_answer_system,
    "tag_only": tag_only_system,
    "tag_single": tag_single_system,
    "tag_templates": tag_templates_system,
    "user_json": user_json,
    "user_templates": user_templates,
}


