import io
import os
from openai import AsyncOpenAI
import requests
import json
import asyncio
import pandas as pd
import re
import math
from prompts import prompts
            
client = AsyncOpenAI()

async def tag_and_answer(texto, cliente, ignore=None, derive=None):
    df_master = pd.read_json(f'./clients/{cliente}/lista_{cliente}.json', orient='index')
    df_master.reset_index(inplace=True)
    df_master.columns = ['Codigo', 'Nombre']  
    df_master["Categoria"] = df_master["Codigo"] + ' - ' + df_master["Nombre"]
    
    # Initialize result string
    result = ""
    for index, row in df_master.iterrows():
        category = row['Categoria']
        result += f"Categoría: {category}\n\n"
    categories = result

    # Build categories string
    categories_str = ""
    for index, row in df_master.iterrows():
        code = row['Codigo']
        name = row['Nombre']
        categories_str += f"{code}: {name}\n"
        
    code_to_category = df_master.set_index('Codigo')['Categoria'].to_dict()
    
    # Prepare optional instruction lines for ignore/derive
    ignore = ignore or []
    derive = derive or []
    ignore_str = ", ".join(ignore) if isinstance(ignore, list) and len(ignore) > 0 else None
    derive_str = ", ".join(derive) if isinstance(derive, list) and len(derive) > 0 else None

    system_message = prompts["tag_and_answer"](categories_str, ignore_str, derive_str)
    user_message = prompts["user_json"](texto)

    try:
        # Call the model
        completion = await client.chat.completions.create(
            model="gpt-4.1",
            temperature=0,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"},
        )

        response_json = json.loads(completion.choices[0].message.content.strip())
        # Special handling for WMI000/WMD000 regardless of presence in lista_{cliente}
        if response_json.get('WMI000', 0) == 1:
            return {'categorias': ['WMI000 - Ignorar'], 'response': "Sin respuesta", 'confidence': 1}
        if response_json.get('WMD000', 0) == 1:
            return {'categorias': ['WMD000 - Derivar'], 'response': "Sin respuesta", 'confidence': 1}
        
        expected_codes = df_master['Codigo'].tolist()
        validated_json = {code: 1 if response_json.get(code, 0) == 1 else 0 for code in expected_codes}
        aplicables = [code_to_category[code] for code, val in validated_json.items() if val == 1]
       
        # Clean the bracketed definitions from aplicables in all cases
        aplicables = [re.sub(r"\s*\[[^\]]*\]\s*", "", cat).strip() for cat in aplicables]
       
        # Load templates
        templates_path = f'./clients/{cliente}/templates_{cliente}.json'
        average_confidence = 0
        try:
            df_templates = pd.read_json(templates_path, orient='index')
            df_templates.columns = ['Template']
        except Exception as e:
            print(f"Error cargando templates: {e}")
            df_templates = pd.DataFrame()

        if len(aplicables) > 1:
            # Extract codes from applicable categories
            codigos_aplicables = [cat.split(' - ')[0] for cat in aplicables]
            
            # Get templates for applicable codes
            templates = []
            for codigo in codigos_aplicables:
                try:
                    template = df_templates.loc[codigo, 'Template']
                    templates.append(f"{codigo}: {template}")
                except KeyError:
                    templates.append(f"{codigo}: Sin respuesta")
            
            # Build templates string for system message
            templates_str = "\n\n".join(templates)
            
            system_message = prompts["tag_templates"](cliente, aplicables, templates_str)
            user_message = prompts["user_templates"](texto)
            completion = await client.chat.completions.create(
                model="gpt-4.1",
                temperature=0.4,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                logprobs=True,
                top_p=0.01
            )

            response = completion.choices[0].message.content
            
            logprobs = completion.choices[0].logprobs.content  # lista de logprobs por token
            confidences = [math.exp(lp.logprob) for lp in logprobs]
            average_confidence = sum(confidences) / len(confidences) if confidences else None
        else:
            try:
                codigos_aplicables = [cat.split(' - ')[0] for cat in aplicables]
                response = df_templates.loc[codigos_aplicables[0], 'Template']
            except (KeyError, IndexError):
                response = "Sin respuesta"

        return {'categorias': aplicables, 'response': response, 'confidence': average_confidence}

    except Exception as e:
        print(f"Error: {e}")
        return {'categorias': ['WMA000 - Otro tipo de Mensaje'], 'response': "Sin respuesta", 'confidence': 0}
    
    
async def tag_only(texto, cliente):

    df_master = pd.read_json(f'./clients/{cliente}/lista_{cliente}.json', orient='index')
    df_master.reset_index(inplace=True)
    df_master.columns = ['Codigo', 'Nombre']  
    df_master["Categoria"] = df_master["Codigo"] + ' - ' + df_master["Nombre"]
    
    # Inicializa una cadena vacía para almacenar el resultado.
    result = ""

    # Itera a través de cada fila en el dataframe maestro.
    for index, row in df_master.iterrows():
        # Extrae la categoría y la definición de cada fila.
        category = row['Categoria']
        
        # Agrega a la cadena resultado.
        result += f"Categoría: {category}\n\n"

    # Asigna la cadena resultado a 'categorias'.
    categories = result

    # Construir cadena de categorías en formato "Código: Nombre"
    categories_str = ""
    for index, row in df_master.iterrows():
        code = row['Codigo']
        name = row['Nombre']
        categories_str += f"{code}: {name}\n"
        
    code_to_category = df_master.set_index('Codigo')['Categoria'].to_dict()
    
    
    system_message = prompts["tag_only"](categories_str)
    user_message = prompts["user_json"](texto)

    try:
        # Completar el texto utilizando el modelo de OpenAI
        completion = await client.chat.completions.create(
            model="gpt-4.1",
            temperature=0,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"},
        )

        response_json = json.loads(completion.choices[0].message.content.strip())
        return response_json
    except Exception as e:
        print(f"Error: {e}")
        return {'error': ['WMA000 - Otro tipo de Mensaje'], 'response': "Sin respuesta"}


async def tag_and_answer_SINGLE(texto, cliente, ignore=None, derive=None):

    df_master = pd.read_json(f'./clients/{cliente}/lista_{cliente}.json', orient='index')
    df_master.reset_index(inplace=True)
    df_master.columns = ['Codigo', 'Nombre']  
    df_master["Categoria"] = df_master["Codigo"] + ' - ' + df_master["Nombre"]
    
    # Inicializa una cadena vacía para almacenar el resultado.
    result = ""

    # Itera a través de cada fila en el dataframe maestro.
    for index, row in df_master.iterrows():
        # Extrae la categoría y la definición de cada fila.
        category = row['Categoria']
        
        # Agrega a la cadena resultado.
        result += f"Categoría: {category}\n\n"

    # Asigna la cadena resultado a 'categorias'.
    categories = result

    # Construir cadena de categorías en formato "Código: Nombre"
    categories_str = ""
    for index, row in df_master.iterrows():
        code = row['Codigo']
        name = row['Nombre']
        categories_str += f"{code}: {name}\n"
        
    code_to_category = df_master.set_index('Codigo')['Categoria'].to_dict()
    
    
    # Prepare optional instruction lines for ignore/derive
    ignore = ignore or []
    derive = derive or []
    ignore_str = ", ".join(ignore) if isinstance(ignore, list) and len(ignore) > 0 else None
    derive_str = ", ".join(derive) if isinstance(derive, list) and len(derive) > 0 else None

    system_message = prompts["tag_single"](categories_str, ignore_str, derive_str)
    user_message = prompts["user_json"](texto)

    try:
        # Completar el texto utilizando el modelo de OpenAI
        completion = await client.chat.completions.create(
            model="gpt-4.1",
            temperature=0,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"},
        )

        response_json = json.loads(completion.choices[0].message.content.strip())

        # Special handling for WMI000/WMD000 regardless of presence in lista_{cliente}
        if response_json.get('WMI000', 0) == 1:
            return {'categorias': ['WMI000 - Ignorar'], 'response': "Sin respuesta"}
        if response_json.get('WMD000', 0) == 1:
            return {'categorias': ['WMD000 - Derivar'], 'response': "Sin respuesta"}
        
        expected_codes = df_master['Codigo'].tolist()
        validated_json = {code: 1 if response_json.get(code, 0) == 1 else 0 for code in expected_codes}
        aplicables = [code_to_category[code] for code, val in validated_json.items() if val == 1]
       
        #tokens += int(completion.usage.prompt_tokens)
        #tokens += int(completion.usage.completion_tokens) * 4
           
        # Cargar templates
        templates_path = f'./clients/{cliente}/templates_{cliente}.json'
        try:
            df_templates = pd.read_json(templates_path, orient='index')
            df_templates.columns = ['Template']  # Asegurar nombre de columna
        except Exception as e:
            print(f"Error cargando templates: {e}")
            df_templates = pd.DataFrame()

        
        if len(aplicables) > 1:
            response = "Sin respuesta"
            return {'categorias': aplicables, 'response':response}
        
        try:
            codigos_aplicables = [cat.split(' - ')[0] for cat in aplicables]
            aplicables = [re.sub(r"\s*\[[^\]]*\]\s*", "", cat).strip() for cat in aplicables]
            response = df_templates.loc[codigos_aplicables[0], 'Template']
        except KeyError:
            response = "Sin respuesta"
        return {'categorias': aplicables, 'response':response}

    except Exception as e:
        print(f"Error: {e}")
        return {'categorias': ['WMA000 - Otro tipo de Mensaje'], 'response': "Sin respuesta"}
