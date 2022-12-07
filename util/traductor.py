import argparse,json,emoji
from collections import Counter
from tqdm import tqdm
import regex as re
from unidecode import unidecode

hizt = {"medC": "medC",
        "treat_therapy": "treatment",
        "env_habitual": "env",
        "other": "other",
        "biochem_substance": "biochem",
        "treat_drug": "treatment",
        "pathogen": "pathogen",
        "env_dietary": "env",
        "qol": "qol",
        "env_socio-economic": "env",
        "diag": "diag",
        "biochem_process": "biochem",
        "env_pollution": "env",
        "env_geo-climate": "env"}

hizt_rel={
            "not_cause_of": "causes",
            "cause_of": "causes",
            "pos_influence_on": "influences",
            "other": "other",
            "treats": "treats",
            "prevents": "prevents",
            "is_type_of": "is_type_of",
            "has_symptom": "has_symptom",
            "neg_influence_on": "influences",
            "pos_interaction": "interaction",
            "side_effect_of": "side_effect_of",
            "may_diagnose": "diagnoses",
            "is_similar_to": "is_similar_to",
            "does_not_treat": "treats",
            "prescribed_for": "treat-medC",
            "may_not_diagnose": "diagnoses",
            "neg_interaction": "interaction",
            "is_contraindicated_drug": "treat-medC",
            "does_not_prevent": "prevents",
            "worsens": "treat-medC"
        }


def token(s):
    s=emoji.demojize(s)
    s=unidecode(s)
    s=re.sub("@user_*","",s)
    s=s.replace("'"," ' ")
    s=s.replace(","," , ")
    s=s.replace("."," . ")
    s=s.replace("?"," ? ")
    s=s.replace("!"," ! ")
    s=s.replace("¿"," ¿ ")
    s=s.replace("¡"," ¡ ")
    s=s.replace("("," ( ")
    s=s.replace(")"," ) ")
    s=s.replace("_"," ")
    s=s.replace("-"," - ")
    s=s.replace(":"," ")
    s=s.replace("#"," ")
    res=s.split()
    cont=0
    for p in res:
        cont+=len(p)
    return res,cont

def tokenizer():
    print('> Creando la traduccion')

    with open(args.filename) as f:
        raw=[json.loads(l) for l in f]

    res=[]

    d_entities=Counter()
    d_relations=Counter()
    borrados=dict()

    for info in tqdm(raw):
        if not 'doc_text' in info:
            borrados[info['doc_id']]='Sin texto'
            continue

        if not 'entities' in info:
            entities=dict()
        else:
            entities=info['entities']
        if not 'relations' in info:
            relations=[]
        else:
            relations=info['relations']
        
        rels=[]
        for r in relations:
            if 'rel_tag' in r and 'start_entity' in r and 'end_entity' in r:
                if r['start_entity'] in entities and r['end_entity'] in entities:
                    aux=dict()
                    aux['type']=r['rel_tag']
                    aux['head']=r['start_entity']
                    aux['tail']=r['end_entity']
                    rels.append(aux)
        key=[]
        ents=[]
        for k,v in entities.items():
            entidad=dict()
            entidad['type']=v['tag']
            entidad['start']=v['begin']
            entidad['end']=v['end']
            ents.append(entidad)
            key.append((k,entidad))
        key.sort(key=lambda x: x[1]['start'])
        ents.sort(key=lambda x: x['start'])
        ordd=dict()
        for i in range(len(key)):
            ordd[key[i][0]]=i
        for r in rels:
            r['head']=ordd[r['head']]
            r['tail']=ordd[r['tail']]
            r['type']=hizt_rel[r['type']]
        flag=False
        ult=0
        for e in ents:
            e['type']=hizt[e['type']]
            if ult>e['start']:
                flag=True
                break
            ult=e['end']
        if flag:
            borrados[info["doc_id"]]="Overlap"
            continue

        texto=info['doc_text']
        texto=texto.replace("[NEWLINE]"," "*9)
        texto=texto.replace("&amp"," &  ")
        l_tks=[]
        inicio=0
        contador=0
        for e in ents:
            tks,cont=token(texto[inicio:e['start']])
            contador+=cont
            l_tks.extend(tks)
            tks,cont=token(texto[e['start']:e['end']])
            e['start']=len(l_tks)
            contador+=cont
            l_tks.extend(tks)
            inicio=e['end']
            e['end']=len(l_tks)
        tks,cont=token(texto[inicio:])
        contador+=cont
        l_tks.extend(tks)
        l_tks.append('.')
        if contador>255:
            borrados[info["doc_id"]]=str(contador)+">255"
            continue
        d_entities.update([x['type'] for x in ents])
        d_relations.update([x['type'] for x in rels])

        aux=dict()
        aux['orig_id']=info['doc_id']
        aux['tokens']=l_tks
        aux['entities']=ents
        aux['relations']=rels
        res.append(aux)

    summary_bear=dict()
    summary_bear["tam"]=len(res)
    summary_bear["n_borrados"]=len(raw)-len(res)
    summary_bear["borrados"]=borrados
    summary_bear["t_entities"]=sum(d_entities.values()) # .total()
    summary_bear["t_relation"]=sum(d_relations.values()) # .total()
    summary_bear["d_entities"]=d_entities
    summary_bear["d_relations"]=d_relations
    summary=dict()
    summary['bear']=summary_bear
    if args.ns:
        with open(args.summary_file, 'w') as fsum:
            json.dump(summary,fsum,indent=4,ensure_ascii=False)
    return res

def summary():
    print('> Creando summary')

    with open(args.summary_file) as f:
        res=json.loads(f.read())
    
    for file in ['train','dev','test']:
        print('\tParte de '+file)

        with open(file+'.json') as f:
            info=json.loads(f.read())

        d_entities=Counter()
        d_relations=Counter()

        for i in info:
            d_entities.update([x['type'] for x in i['entities']])
            d_relations.update([x['type'] for x in i['relations']])

        x=dict()
        x["total"]=len(info)
        x["t_entidades"]=sum(d_entities.values())
        x["t_relatios"]=sum(d_relations.values())
        x["entities"]=d_entities
        x["relation"]=d_relations
        res[file]=x

    with open(args.summary_file, 'w') as f:
        json.dump(res,f,indent=4,ensure_ascii=False)

def create_types():
    print('> Creando types.json')

    res=dict()
    ent=dict()
    rel=dict()
    for i in res:
        for e in i["entities"]:
            aux=dict()
            aux["short"]=e["type"]
            aux["verbose"]=e["type"]
            ent[e["type"]]=aux
        for e in i["relations"]:
            aux=dict()
            aux["short"]=e["type"]
            aux["verbose"]=e["type"]
            aux["symmetric"]=False
            rel[e["type"]]=aux

    res["entities"]=ent
    res["relations"]=rel
    with open('types.json', 'w') as fres:
        json.dump(res,fres,indent=4,ensure_ascii=False)

def create_partition():
    print('> Creando las particiones')

    # Tamaño de las distribuciones
    p_test,p_dev=0.1, 0.1

    train=[]
    dev=[]
    test=[]

    h={
        "medC": [],
        "treatment": [],
        "env": [],
        "other": [],
        "biochem": [],
        "pathogen": [],
        "qol": [],
        "diag": [],
        "null": []
    }
    prioridad={
        "medC": 7,
        "treatment": 6,
        "env": 4,
        "other": 3,
        "biochem": 5,
        "pathogen": 1,
        "qol": 2,
        "diag": 0,
        "null": 8
    }
    clases=["diag","pathogen","qol","other","env","biochem","treatment","medC","null"]

    # Clasificacion de los tweets segun su entidad mas especial
    for i in res:
        val=8
        for e in i["entities"]:
            if prioridad[e["type"]]<val:
                val=prioridad[e["type"]]
        h[clases[val]].append(i)
    # Reparto de los tweets por entidades
    for k in clases:
        x=h[k]
        p1=int(len(x)*p_test)
        p2=p1+int(len(x)*p_dev)
        test.extend(x[:p1])
        dev.extend(x[p1:p2])
        train.extend(x[p2:])

    with open('train.json', 'w') as ftrain:
        json.dump(train,ftrain,indent=4,ensure_ascii=False)
    with open('dev.json', 'w') as fdev:
        json.dump(dev,fdev,indent=4,ensure_ascii=False)
    with open('test.json', 'w') as ftest:
        json.dump(test,ftest,indent=4,ensure_ascii=False)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Traducir bear.jsonl a bear.json')
    # > bear.jsonl
    # < bear.json   
    # < summary.json   
    # < train.json   dev.json    text.json    
    # < types.json
    parser.add_argument('-f', metavar='filename',dest='filename',action='store',help='nombre del fichero origen, default bear.jsonl',default='bear.jsonl')    
    parser.add_argument('-df', metavar='dest_filename',dest='dest_filename',action='store',help='nombre para el fichero final, default bear.json',default='bear.json')
    parser.add_argument('-ns', action='store_false',help='crear fichero summary, default true',default=True)
    parser.add_argument('-sf', metavar='summary_file',dest='summary_file',action='store',help='nombre para el fichero summary, default summary.json',default='summary.json')
    parser.add_argument('-np', action='store_false',help='crear particiones, default true',default=True)
    parser.add_argument('-nt', action='store_false',help='crear types, default true',default=True)
    args = parser.parse_args()
    
    res = tokenizer()
    with open(args.dest_filename, 'w') as f:
        json.dump(res,f,indent=4,ensure_ascii=False)

    if args.np:
        create_types()
    
    if args.nt:
        create_types()
    
    if args.ns:
        summary()