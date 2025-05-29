# Continuous-Auditing--Supply

Este projeto implementa um sistema de **Auditoria Contínua** voltado à **cadeia de suprimentos**, com foco em análise de contratos, detecção de possíveis irregularidades e visualização de dados via dashboard interativo.

Desenvolvido em **Django** (backend) e **HTML/CSS/JS** (frontend), este sistema permite o upload de planilhas (.xlsx) com dados contratuais e aplica regras de auditoria automatizadas com base em parâmetros fiscais e de mercado.

## 🎯 Objetivos

- Automatizar a auditoria de contratos com base em valores de mercado e tributos.
- Detectar possíveis contratos irregulares.
- Disponibilizar um painel de análise gerencial.
- Possibilitar integração futura com APIs externas (e.g., dados fiscais e de mercado).

## ⚙️ Estrutura do Projeto

Continuous-Auditing--Supply/
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
├── Procfile
├── README.md
├── seu_projeto_auditoria/
│   ├── seu_projeto_principal/
│   └── seu_app/
│       ├── templates/
│       ├── static/
│       ├── audit_rules.py
│       ├── views.py, urls.py, etc.
├── media/
└── temp_uploads/

## 🚀 Como executar localmente

```bash
git clone https://github.com/jsalexandremg/Continuous-Auditing--Supply.git
cd Continuous-Auditing--Supply
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/` no navegador.

## 👨‍💼 Autor

**Jeferson Alexandre**  
Auditor Interno — Idealizador do Continuous Auditing Supply  
[GitHub: @jsalexandremg](https://github.com/jsalexandremg)