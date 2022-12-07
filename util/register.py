import argparse,json
import pandas as pd

def iniTop():
    top=dict()
    ner_row=['ner_prec_micro','ner_rec_micro','ner_prec_macro','ner_rec_macro','ner_f1_micro','ner_f1_macro']
    rel_row=['rel_prec_micro','rel_rec_micro','rel_prec_macro','rel_rec_macro','rel_f1_micro','rel_f1_macro']
    rel_neq_row=['rel_nec_prec_micro','rel_nec_rec_micro','rel_nec_prec_macro','rel_nec_rec_macro','rel_nec_f1_micro','rel_nec_f1_macro']
    for x in ner_row:
        top[x]=[0,""]
    for x in rel_row:
        top[x]=[0,""]
    for x in rel_neq_row:
        top[x]=[0,""]
    res=dict()
    res['top']=top
    return res

def addEval():
    print('> Añadiendo el rendimiendo al resumen')

    try:
        with open(args.models_file) as f:
            res=json.loads(f.read())
    except:
        print('\t*Creando top inicial')
        res=iniTop()
    est=dict()

    for part in ['train','dev','test']:
        aux=dict()
        with open(part+'.csv') as f:
            tipo=f.readline().split(';')
            val=f.readline().split(';')
            for t,v in zip(tipo,val):
                aux[t]=round(float(v),2)
        est[part]=aux

    res[args.model]=est
    with open(args.models_file, 'w') as f:
        json.dump(res,f,indent=4,ensure_ascii=False)    

def addTop():
    print('> Comparando el rendimiento con el top')

    with open(args.models_file) as f:
        res=json.loads(f.read())
    for k,v in res['top'].items():
        if v[0]<res[args.model]['test'][k]:
            res['top'][k]=[res[args.model]['test'][k],args.model]
            print('\t Mejora de rendimiento en:',k)
    with open(args.models_file, 'w') as f:
        json.dump(res,f,indent=4,ensure_ascii=False) 

def addTabla():
    print('> Creando tablas de rendimientos')

    with open(args.models_file) as f:
        res=json.loads(f.read())

    modelos=list(res.keys())
    modelos.remove('top')
    ner_row=['ner_prec_micro','ner_rec_micro','ner_prec_macro','ner_rec_macro','ner_f1_micro','ner_f1_macro']
    rel_row=['rel_prec_micro','rel_rec_micro','rel_prec_macro','rel_rec_macro','rel_f1_micro','rel_f1_macro']
    rel_neq_row=['rel_nec_prec_micro','rel_nec_rec_micro','rel_nec_prec_macro','rel_nec_rec_macro','rel_nec_f1_micro','rel_nec_f1_macro']
    data_ner=dict()
    data_rel=dict()
    data_rel_neq=dict()
    for model in modelos:
        aux=[]
        for r in ner_row:
            aux.append(res[model]['test'][r])
        data_ner[model]=aux
        aux=[]
        for r in rel_row:
            aux.append(res[model]['test'][r])
        data_rel[model]=aux
        aux=[]
        for r in rel_neq_row:
            aux.append(res[model]['test'][r])
        data_rel_neq[model]=aux
    df=pd.DataFrame(data_ner,index=ner_row)
    df.to_csv('tabla_ner.csv')
    df=pd.DataFrame(data_rel,index=rel_row)
    df.to_csv('tabla_rel.csv')
    df=pd.DataFrame(data_rel_neq,index=rel_neq_row)
    df.to_csv('tabla_rel_neq.csv')

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Realiza la evaluacion del rendimiento del modelo.')
    # > [models.json]    train.csv   dev.csv     test.csv
    # < models.json    tabla_ner.csv   tabla_rel.csv   tabla_rel_neq.csv
    parser.add_argument('model', help='nombre del modelo')
    parser.add_argument('-rf', metavar='models_file',dest='models_file',action='store',help='nombre para el registro de rendimiento, default models.json',default='models.json')
    parser.add_argument('-t', action='store_true',help='crear las tablas de comparacion, default false')
    args = parser.parse_args()
    
    if args.t:
        addTabla()
    else:
        print('Analizando el rendimiento de',args.model)
        addEval()
        addTop()