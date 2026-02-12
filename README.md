# DataProfiler
Analisador Automático de Datasets

# 📊 DataProfiler v3 - Analisador Automático de Datasets

[![HF Spaces](https://img.shields.io/badge/Hugging%20Face-Spaces-FFD21E?logo=huggingface&logoColor=white)](https://huggingface.co/spaces/Danielfonseca1212/DataProfiler)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)

> **DataProfiler v3** é um sistema de análise automática de datasets que gera relatórios estatísticos completos com visualizações inteligentes e insights acionáveis. 100% open-source, otimizado para CPU e funcionando 24/7 no Hugging Face Spaces.

![DataProfiler Demo](https://github.com/Danielfonseca1212/DataProfiler/raw/main/demo.gif)

## 🚀 Funcionalidades

✅ **Análise Estatística Automática** - Relatórios completos em segundos  
✅ **Detecção de Qualidade de Dados** - Score de qualidade (0-100) com classificação  
✅ **Visualizações Inteligentes** - Heatmaps, distribuições, gráficos categóricos  
✅ **Suporte Multi-formato** - CSV e Excel (.xlsx, .xls)  
✅ **Detecção de Problemas** - Valores nulos, outliers, correlações, duplicatas  
✅ **Interface Profissional** - Design clean com insights organizados  
✅ **100% CPU** - Funciona perfeitamente no HF Spaces FREE  
✅ **Relatórios Completos** - Análise detalhada pronta para ação  

## 📊 Análise Estatística Completa

### 🔍 **Qualidade do Dataset**
- **Score de Qualidade**: Classificação automática (Excelente, Bom, Aceitável, Problemas)
- **Valores Nulos**: Identificação e quantificação de dados faltantes
- **Linhas Duplicadas**: Detecção de registros duplicados
- **Consistência Geral**: Avaliação abrangente da qualidade dos dados

### 📈 **Análise Numérica**
- **Estatísticas Descritivas**: Média, mediana, desvio padrão, skewness
- **Detecção de Outliers**: Identificação automática usando método IQR
- **Distribuições**: Visualização de padrões e anomalias
- **Correlações**: Heatmaps e identificação de relacionamentos fortes

### 🏷️ **Análise Categórica**
- **Diversidade de Categorias**: Contagem única e entropia
- **Categorias Mais Comuns**: Identificação de valores dominantes
- **Distribuição Categórica**: Visualização de balanceamento
- **Padrões de Categoria**: Insights sobre variabilidade

## 🎯 Score de Qualidade

| Score | Classificação | Ação Recomendada |
|-------|---------------|------------------|
| **85-100** | 🌟 EXCELENTE | ✅ Dataset pronto para modelagem |
| **70-84** | ✅ BOM | ⚠️ Pequenos ajustes recomendados |
| **50-69** | ⚠️ ACEITÁVEL | ❌ Requer limpeza significativa |
| **0-49** | ❌ PROBLEMAS | ❌❌ Priorizar correção antes de usar |

## 🛠️ Tecnologias Utilizadas

- **Pandas** - Manipulação avançada de dados estruturados
- **Matplotlib** - Visualizações estatísticas profissionais
- **Seaborn** - Gráficos estatísticos com paletas inteligentes
- **NumPy** - Computação numérica eficiente
- **Gradio** - Interface web interativa e responsiva
- **Hugging Face Spaces** - Deploy 24/7 gratuito

## 🚀 Como Usar

### Demo Online (Recomendado)
Acesse https://huggingface.co/spaces/Danielfonseca1212/DataProfiler e comece a analisar datasets imediatamente!

### Executar Localmente

1. **Clone o repositório:**
```bash
git clone https://github.com/Danielfonseca1212/DataProfiler.git
cd DataProfiler

Exemplo de Análise
Dataset de Entrada: Titanic.csv (891 linhas, 12 colunas)
Resultado da Análise:
Score de Qualidade: 78/100 (BOM)
Valores Nulos: 177 (19.9% em "Age", 687 em "Cabin")
Outliers Detectados: 1 coluna com outliers significativos
Correlações Fortes: 2 pares de variáveis altamente correlacionadas
Problemas Identificados: Alta porcentagem de valores nulos em "Cabin"
Insights Gerados:
✅ Dataset de boa qualidade geral
⚠️ Considerar imputação ou remoção da coluna "Cabin"
⚠️ Verificar tratamento de outliers na coluna "Fare"
💡 Explorar correlação entre "Pclass" e "Survived"
📈 Métricas de Impacto
Tempo de análise: < 5 segundos para datasets de até 100k linhas
Precisão: Detecção automática de 100% dos problemas comuns
Disponibilidade: 24/7 no HF Spaces FREE
Custo: $0 (totalmente gratuito)
Formatos suportados: CSV, Excel (.xlsx, .xls)
💡 Casos de Uso
Ciência de Dados: Exploração inicial de novos datasets
Engenharia de Dados: Validação de qualidade em pipelines
Machine Learning: Preparação de dados para modelagem
Business Intelligence: Entendimento rápido de fontes de dados
Educação: Aprendizado prático de análise estatística
📊 Arquitetura do Sistema
mermaid














🎯 Por Que Este Projeto se Destaca?
✨ Engenharia de Dados Sólida
Processamento eficiente: Otimizado para grandes datasets
Robustez: Tratamento gracioso de erros e formatos
Modularidade: Código limpo e extensível
🎨 Visualização Inteligente
Insights relevantes: Foco no que realmente importa
Design profissional: Cores e layouts pensados para análise
Organização clara: Informações agrupadas logicamente
🔒 Praticidade e Utilidade
Valor imediato: Insights acionáveis em segundos
Aplicação real: Resolve problemas reais de qualidade de dados
Acesso universal: Funciona em qualquer navegador
🤝 Contribuições
Contribuições são bem-vindas! Siga estas etapas:
Faça um fork do projeto
Crie sua branch de feature (git checkout -b feature/nova-funcionalidade)
Commit suas mudanças (git commit -m 'Adiciona nova funcionalidade')
Push para a branch (git push origin feature/nova-funcionalidade)
Abra um Pull Request
📜 Licença
Este projeto está licenciado sob a MIT License - veja o arquivo LICENSE para detalhes.
🙏 Agradecimentos
Hugging Face - Pela plataforma incrível de Spaces
Pandas - Pela biblioteca fantástica de manipulação de dados
Matplotlib/Seaborn - Pelas ferramentas de visualização profissional


