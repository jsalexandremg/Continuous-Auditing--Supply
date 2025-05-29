from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .audit_rules import verificar_valor_vs_mercado
import pandas as pd

def upload_auditoria(request):
    if request.method == 'POST' and request.FILES['excel_file']:
        file = request.FILES['excel_file']
        fs = FileSystemStorage(location='temp_uploads/')
        filename = fs.save(file.name, file)
        file_path = fs.path(filename)

        df = pd.read_excel(file_path)
        resultados = []
        for index, row in df.iterrows():
            alerta = verificar_valor_vs_mercado(row, valor_mercado=1000, impostos=17)
            if alerta:
                resultados.append({**row, 'alerta': alerta})
        return render(request, 'dashboard_auditoria.html', {'resultados': resultados})

    return render(request, 'upload_auditoria.html')
