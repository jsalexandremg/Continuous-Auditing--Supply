# Pacote para Deploy Próprio e Auditoria Contínua

Este pacote contém todos os arquivos necessários para executar o dashboard de análise de preços em seu próprio ambiente. Isso permite que você realize auditorias contínuas e personalize o dashboard conforme suas necessidades.

## Conteúdo do Pacote

1. **Dashboard Simplificado (HTML/JS)**
   - `dashboard_simplified/` - Versão simplificada do dashboard em HTML/JS puro
   - Pode ser hospedado em qualquer servidor web estático

2. **Dashboard Completo (Python/Dash)**
   - `dashboard_complete/` - Versão completa do dashboard usando Python, Pandas e Dash
   - Oferece mais recursos analíticos, mas requer ambiente Python

3. **Scripts de Análise**
   - `scripts/` - Scripts Python para análise de dados e detecção de outliers
   - Útil para processamento em lote ou integração com outros sistemas

4. **Dados de Exemplo**
   - `data/` - Arquivos de dados de exemplo para teste
   - Inclui dados originais, resultados de análise e comparações externas

## Instruções de Uso

### Dashboard Simplificado (HTML/JS)

1. **Requisitos:**
   - Qualquer servidor web estático (Apache, Nginx, IIS, etc.)
   - Ou simplesmente abra os arquivos localmente em um navegador

2. **Instalação:**
   - Copie o conteúdo da pasta `dashboard_simplified/` para seu servidor web
   - Ou abra o arquivo `index.html` diretamente em seu navegador

3. **Personalização:**
   - Edite o arquivo `data.js` para incluir seus próprios dados
   - Modifique o arquivo `app.js` para ajustar a lógica de filtragem ou visualização
   - Adapte o arquivo `index.html` para alterar o layout ou estilo

### Dashboard Completo (Python/Dash)

1. **Requisitos:**
   - Python 3.11 ou superior
   - Bibliotecas: pandas, dash, plotly, numpy, openpyxl

2. **Instalação:**
   ```bash
   # Criar ambiente virtual
   python -m venv venv
   
   # Ativar ambiente virtual
   # No Windows:
   venv\Scripts\activate
   # No Linux/Mac:
   source venv/bin/activate
   
   # Instalar dependências
   pip install -r requirements.txt
   ```

3. **Execução:**
   ```bash
   python app.py
   ```
   O dashboard estará disponível em http://localhost:8050

4. **Personalização:**
   - Edite o arquivo `app.py` para modificar a lógica do dashboard
   - Substitua os arquivos em `data/` com seus próprios dados
   - Ajuste os parâmetros de análise em `scripts/analyze_prices.py`

### Scripts de Análise

1. **Análise de Preços:**
   ```bash
   python scripts/analyze_prices.py --input data/seu_arquivo.xlsx --output data/resultados.csv
   ```

2. **Detecção de Outliers:**
   ```bash
   python scripts/detect_outliers.py --input data/seu_arquivo.xlsx --output data/outliers.csv
   ```

3. **Geração de Relatório:**
   ```bash
   python scripts/generate_report.py --input data/resultados.csv --output relatorio.html
   ```

## Integração com Sistemas Existentes

### Importação de Dados

O dashboard pode ser alimentado com dados de diversas fontes:

1. **Arquivos Excel:**
   - Coloque seus arquivos Excel na pasta `data/`
   - Use o script `scripts/import_excel.py` para converter para o formato necessário

2. **Bancos de Dados:**
   - Modifique o script `scripts/import_database.py` para conectar ao seu banco de dados
   - Configure as credenciais em `config/database.ini`

3. **APIs:**
   - Use o script `scripts/import_api.py` para obter dados de APIs externas
   - Configure os endpoints em `config/api.ini`

### Exportação de Resultados

Os resultados da análise podem ser exportados em vários formatos:

1. **CSV/Excel:**
   - Use o botão "Exportar CSV" no dashboard
   - Ou execute `scripts/export_results.py --format excel`

2. **Relatórios PDF:**
   - Execute `scripts/generate_pdf.py` para criar relatórios em PDF
   - Personalize o template em `templates/report_template.html`

3. **Integração com BI:**
   - Os dados podem ser exportados para ferramentas de BI como Power BI ou Tableau
   - Use `scripts/export_for_bi.py` para formatar os dados adequadamente

## Manutenção e Atualização

### Atualização de Dados

Para manter o dashboard atualizado com novos dados:

1. **Atualização Manual:**
   - Substitua os arquivos em `data/` com novos dados
   - Execute `scripts/update_dashboard.py` para atualizar as visualizações

2. **Atualização Automática:**
   - Configure um job agendado (cron, Task Scheduler) para executar `scripts/auto_update.py`
   - Defina a frequência de atualização em `config/schedule.ini`

### Backup

Recomendamos fazer backup regular dos seus dados e configurações:

1. **Backup Manual:**
   - Execute `scripts/backup.py` para criar um arquivo ZIP com todos os dados e configurações

2. **Backup Automático:**
   - Configure um job agendado para executar `scripts/auto_backup.py`
   - Os backups serão armazenados em `backups/` com timestamp

## Suporte e Recursos Adicionais

Para obter mais informações ou suporte:

1. **Documentação:**
   - Consulte a pasta `docs/` para documentação detalhada
   - Veja exemplos de uso em `examples/`

2. **Resolução de Problemas:**
   - Verifique `docs/troubleshooting.md` para soluções de problemas comuns
   - Use `scripts/diagnostics.py` para verificar a integridade do sistema

## Licença e Uso

Este pacote é fornecido para uso interno da sua organização. Todos os direitos reservados.

---

Esperamos que este pacote seja útil para suas necessidades de auditoria contínua. Se tiver dúvidas ou precisar de assistência adicional, não hesite em entrar em contato.
