"""
DataProfiler v3.0 - Analisador Automático de Datasets
✅ 100% CPU • Relatórios estatísticos automáticos • Visualizações inteligentes
"""

import os
import warnings
warnings.filterwarnings('ignore')

os.environ['TOKENIZERS_PARALLELISM'] = 'false'

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import gradio as gr

# Configurações de estilo
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class DataProfiler:
    """Analisa datasets automaticamente gerando relatórios estatísticos"""
    
    def __init__(self):
        pass
    
    def analyze_dataset(self, file_path):
        """Analisa dataset e retorna estatísticas completas"""
        try:
            # Carregar dataset
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            if df.empty:
                return {"error": "Dataset vazio"}
            
            # Estatísticas básicas
            stats = {
                'shape': df.shape,
                'missing_values': int(df.isnull().sum().sum()),
                'duplicate_rows': int(df.duplicated().sum()),
                'numeric_columns': df.select_dtypes(include=[np.number]).shape[1],
                'categorical_columns': df.select_dtypes(include=['object']).shape[1],
                'datetime_columns': df.select_dtypes(include=['datetime64']).shape[1]
            }
            
            # Análise detalhada por tipo de coluna
            analysis = {
                'numeric_stats': self._analyze_numeric_columns(df),
                'categorical_stats': self._analyze_categorical_columns(df),
                'missing_patterns': self._analyze_missing_data(df),
                'correlations': self._analyze_correlations(df),
                'outliers': self._detect_outliers(df)
            }
            
            return {
                'stats': stats,
                'analysis': analysis,
                'sample': df.head().to_html(classes='table table-striped', escape=False),
                'columns': list(df.columns),
                'dtypes': df.dtypes.to_dict()
            }
            
        except Exception as e:
            return {"error": f"Erro ao analisar dataset: {str(e)[:150]}"}
    
    def _analyze_numeric_columns(self, df):
        """Análise de colunas numéricas"""
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            return None
        
        stats = {}
        for column in numeric_df.columns:
            series = numeric_df[column].dropna()
            if len(series) > 0:
                stats[column] = {
                    'mean': float(series.mean()),
                    'median': float(series.median()),
                    'std': float(series.std()),
                    'min': float(series.min()),
                    'max': float(series.max()),
                    'skewness': float(series.skew()),
                    'has_outliers': self._has_outliers_iqr(series)
                }
        
        return stats
    
    def _analyze_categorical_columns(self, df):
        """Análise de colunas categóricas"""
        categorical_df = df.select_dtypes(include=['object'])
        if categorical_df.empty:
            return None
        
        stats = {}
        for column in categorical_df.columns:
            series = categorical_df[column].dropna()
            if len(series) > 0:
                value_counts = series.value_counts()
                stats[column] = {
                    'unique_values': int(series.nunique()),
                    'most_common': str(value_counts.index[0]) if len(value_counts) > 0 else "N/A",
                    'most_common_count': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                    'entropy': float(self._calculate_entropy(series))
                }
        
        return stats
    
    def _analyze_missing_data(self, df):
        """Análise de dados faltantes"""
        missing_data = df.isnull().sum()
        missing_data = missing_data[missing_data > 0].sort_values(ascending=False)
        
        if missing_data.empty:
            return {'has_missing': False, 'missing_columns': []}
        
        # Calcular padrão de missing data
        missing_matrix = df.isnull()
        missing_correlation = missing_matrix.corr() if len(missing_matrix.columns) > 1 else None
        
        return {
            'has_missing': True,
            'missing_columns': missing_data.to_dict(),
            'total_missing': int(missing_data.sum()),
            'missing_percentage': float((missing_data.sum() / len(df)) * 100)
        }
    
    def _analyze_correlations(self, df):
        """Análise de correlações"""
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.shape[1] < 2:
            return None
        
        correlation_matrix = numeric_df.corr()
        # Encontrar correlações fortes (> 0.7 ou < -0.7)
        strong_correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:
                    strong_correlations.append({
                        'col1': correlation_matrix.columns[i],
                        'col2': correlation_matrix.columns[j],
                        'correlation': float(corr_value)
                    })
        
        return {
            'matrix': correlation_matrix,
            'strong_correlations': strong_correlations,
            'count_strong': len(strong_correlations)
        }
    
    def _detect_outliers(self, df):
        """Detecção de outliers usando IQR"""
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            return {'has_outliers': False, 'outlier_columns': []}
        
        outlier_columns = []
        for column in numeric_df.columns:
            series = numeric_df[column].dropna()
            if len(series) > 0:
                Q1 = series.quantile(0.25)
                Q3 = series.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers = series[(series < lower_bound) | (series > upper_bound)]
                if len(outliers) > 0:
                    outlier_columns.append({
                        'column': column,
                        'outlier_count': len(outliers),
                        'percentage': float((len(outliers) / len(series)) * 100)
                    })
        
        return {
            'has_outliers': len(outlier_columns) > 0,
            'outlier_columns': outlier_columns
        }
    
    def _has_outliers_iqr(self, series):
        """Verifica se série tem outliers usando IQR"""
        if len(series) < 4:
            return False
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return ((series < lower_bound) | (series > upper_bound)).any()
    
    def _calculate_entropy(self, series):
        """Calcula entropia de uma série categórica"""
        if len(series) == 0:
            return 0
        value_counts = series.value_counts()
        probabilities = value_counts / len(series)
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        return entropy
    
    def generate_visualizations(self, df, analysis):
        """Gera visualizações para o dataset"""
        plots = {}
        
        # 1. Distribuição de valores nulos
        if analysis['missing_patterns']['has_missing']:
            plt.figure(figsize=(10, 6))
            missing_data = pd.Series(analysis['missing_patterns']['missing_columns'])
            if len(missing_data) > 10:
                missing_data = missing_data.head(10)
            missing_data.plot(kind='bar', color='#d32f2f')
            plt.title('Valores Nulos por Coluna (Top 10)')
            plt.xlabel('Colunas')
            plt.ylabel('Contagem de Valores Nulos')
            plt.xticks(rotation=45, ha='right')
            plots['missing'] = self._fig_to_base64(plt.gcf())
            plt.close()
        
        # 2. Correlação (se houver colunas numéricas suficientes)
        if analysis['correlations'] is not None and len(analysis['correlations']['matrix']) > 1:
            plt.figure(figsize=(10, 8))
            correlation_matrix = analysis['correlations']['matrix']
            # Limitar a 10x10 para evitar gráficos muito grandes
            if len(correlation_matrix) > 10:
                correlation_matrix = correlation_matrix.iloc[:10, :10]
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                       fmt='.2f', square=True, cbar_kws={'shrink': .8})
            plt.title('Matriz de Correlação')
            plt.tight_layout()
            plots['correlation'] = self._fig_to_base64(plt.gcf())
            plt.close()
        
        # 3. Distribuição das colunas numéricas (top 4)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            cols_to_plot = numeric_cols[:4]
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            axes = axes.flatten()
            
            for i, col in enumerate(cols_to_plot):
                df[col].hist(bins=30, ax=axes[i], color='#1976d2', alpha=0.7)
                axes[i].set_title(f'Distribuição: {col}')
                axes[i].set_xlabel(col)
                axes[i].set_ylabel('Frequência')
            
            # Esconder subplots vazios
            for i in range(len(cols_to_plot), 4):
                axes[i].set_visible(False)
            
            plt.tight_layout()
            plots['distribution'] = self._fig_to_base64(plt.gcf())
            plt.close()
        
        # 4. Contagem das colunas categóricas (top 2)
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            cols_to_plot = categorical_cols[:2]
            fig, axes = plt.subplots(1, 2, figsize=(15, 6))
            if len(cols_to_plot) == 1:
                axes = [axes]
            
            for i, col in enumerate(cols_to_plot):
                top_categories = df[col].value_counts().head(8)
                top_categories.plot(kind='bar', ax=axes[i], color='#388e3c', alpha=0.7)
                axes[i].set_title(f'Top Categorias: {col}')
                axes[i].set_xlabel('Categorias')
                axes[i].set_ylabel('Contagem')
                axes[i].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            plots['categorical'] = self._fig_to_base64(plt.gcf())
            plt.close()
        
        return plots
    
    def _fig_to_base64(self, fig):
        """Converte figura matplotlib para base64"""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode()
        return f"data:image/png;base64,{img_str}"

def profile_dataset(file):
    """Função principal para interface Gradio"""
    if file is None:
        return (
            "<div style='color:#d32f2f; padding:20px; text-align:center; background:#ffebee; border-radius:12px; font-size:16px; font-weight:bold;'>⚠️ Faça upload de um arquivo CSV ou Excel</div>",
            "", "", ""
        )
    
    try:
        profiler = DataProfiler()
        result = profiler.analyze_dataset(file.name)
        
        if 'error' in result:
            return (
                f"<div style='color:#c62828; padding:20px; background:#ffebee; border-radius:12px; font-size:15px; font-weight:bold; text-align:center;'>❌ {result['error']}</div>",
                "", "", ""
            )
        
        # Gerar visualizações
        df = pd.read_csv(file.name) if file.name.endswith('.csv') else pd.read_excel(file.name)
        plots = profiler.generate_visualizations(df, result['analysis'])
        
        # Criar HTML do resultado
        resultado_html = create_result_html(result, plots)
        
        return resultado_html, "", "", ""
        
    except Exception as e:
        erro_html = f"""
        <div style='color:#c62828; padding:25px; background:#ffebee; border-radius:16px; font-size:16px; line-height:1.6; text-align:center;'>
            <div style='font-weight:bold; margin-bottom:15px; font-size:20px;'>❌ Erro durante análise</div>
            <div style='font-family:monospace; background:#ffcdd2; padding:15px; border-radius:10px; margin-top:10px;'>
                {str(e)[:200]}
            </div>
            <div style='margin-top:15px; font-size:14px; color:#546e7a;'>
                💡 Dica: Verifique se o arquivo CSV/Excel está formatado corretamente.
            </div>
        </div>
        """
        return erro_html, "", "", ""

def create_result_html(result, plots):
    """Cria HTML com resultado da análise"""
    stats = result['stats']
    
    # Classificar qualidade do dataset
    quality_score = calculate_quality_score(stats, result['analysis'])
    quality_colors = {
        'EXCELENTE': '#2E7D32',
        'BOM': '#7CB342', 
        'ACEITÁVEL': '#F57C00',
        'PROBLEMAS': '#D32F2F'
    }
    
    quality_emoji = {
        'EXCELENTE': '🌟',
        'BOM': '✅',
        'ACEITÁVEL': '⚠️',
        'PROBLEMAS': '❌'
    }
    
    resultado_html = f"""
    <div style='max-width:900px; margin:0 auto; font-family:Segoe UI, system-ui;'>
        <!-- QUALIDADE GERAL -->
        <div style='text-align:center; background:{quality_colors[quality_score]}08; border-radius:20px; padding:25px; margin-bottom:25px; border:2px solid {quality_colors[quality_score]}25;'>
            <div style='font-size:60px; margin-bottom:15px;'>{quality_emoji[quality_score]}</div>
            <h2 style='color:{quality_colors[quality_score]}; font-size:32px; margin:0 0 15px 0; font-weight:800;'>Qualidade: {quality_score}</h2>
            <div style='font-size:24px; font-weight:700; color:{quality_colors[quality_score]}; margin-bottom:15px;'>
                Dataset de {"alta" if quality_score in ["EXCELENTE", "BOM"] else "baixa"} qualidade
            </div>
            <div style='width:100%; max-width:360px; height:22px; background:rgba(0,0,0,0.08); border-radius:11px; margin:0 auto 18px; overflow:hidden;'>
                <div style='width:{get_quality_percentage(quality_score)}%; height:100%; background:{quality_colors[quality_score]}; border-radius:11px;'></div>
            </div>
        </div>
        
        <!-- ESTATÍSTICAS BÁSICAS -->
        <div style='background:#f5f5f5; border-radius:16px; padding:20px; margin-bottom:25px;'>
            <h3 style='color:#424242; margin:0 0 15px 0; font-size:22px;'>📊 Estatísticas Básicas</h3>
            <div style='display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap:15px;'>
                <div style='text-align:center;'>
                    <div style='font-size:28px; font-weight:700; color:#1976D2;'>{stats['shape'][0]:,}</div>
                    <div style='color:#616161; font-size:14px;'>Linhas</div>
                </div>
                <div style='text-align:center;'>
                    <div style='font-size:28px; font-weight:700; color:#1976D2;'>{stats['shape'][1]}</div>
                    <div style='color:#616161; font-size:14px;'>Colunas</div>
                </div>
                <div style='text-align:center;'>
                    <div style='font-size:28px; font-weight:700; color:#D32F2F;'>{stats['missing_values']:,}</div>
                    <div style='color:#616161; font-size:14px;'>Valores Nulos</div>
                </div>
                <div style='text-align:center;'>
                    <div style='font-size:28px; font-weight:700; color:#F57C00;'>{stats['duplicate_rows']:,}</div>
                    <div style='color:#616161; font-size:14px;'>Linhas Duplicadas</div>
                </div>
            </div>
        </div>
    """
    
    # Seções detalhadas
    sections = []
    
    # Valores nulos
    if result['analysis']['missing_patterns']['has_missing']:
        sections.append(('missing', 'Valores Nulos', '#D32F2F'))
    
    # Correlações
    if result['analysis']['correlations'] is not None and result['analysis']['correlations']['count_strong'] > 0:
        sections.append(('correlation', 'Correlações Fortes', '#1976D2'))
    
    # Outliers
    if result['analysis']['outliers']['has_outliers']:
        sections.append(('outliers', 'Outliers Detectados', '#F57C00'))
    
    # Colunas numéricas
    if result['analysis']['numeric_stats'] is not None:
        sections.append(('numeric', 'Análise Numérica', '#388E3C'))
    
    # Colunas categóricas  
    if result['analysis']['categorical_stats'] is not None:
        sections.append(('categorical', 'Análise Categórica', '#7B1FA2'))
    
    for section_key, section_name, color in sections:
        resultado_html += f"""
        <div style='background:#f5f5f5; border-radius:16px; padding:20px; margin-bottom:20px; border-left:4px solid {color};'>
            <h3 style='color:{color}; margin:0 0 15px 0; font-size:22px;'>{section_name}</h3>
        """
        
        if section_key == 'missing':
            missing_info = result['analysis']['missing_patterns']
            resultado_html += f"""
            <p><strong>Total de valores nulos:</strong> {missing_info['total_missing']:,} ({missing_info['missing_percentage']:.1f}%)</p>
            <div style='max-height:200px; overflow-y:auto; margin-top:10px;'>
                <table style='width:100%; border-collapse:collapse;'>
                    <thead><tr style='background:{color}10;'>
                        <th style='padding:8px; text-align:left; border-bottom:2px solid {color}30;'>Coluna</th>
                        <th style='padding:8px; text-align:right; border-bottom:2px solid {color}30;'>Valores Nulos</th>
                    </tr></thead>
                    <tbody>
            """
            for col, count in list(missing_info['missing_columns'].items())[:10]:
                resultado_html += f"""
                    <tr style='border-bottom:1px solid #e0e0e0;'>
                        <td style='padding:8px;'>{col}</td>
                        <td style='padding:8px; text-align:right;'>{count:,}</td>
                    </tr>
                """
            resultado_html += """
                    </tbody>
                </table>
            </div>
            """
            
            if 'missing' in plots:
                resultado_html += f"<img src='{plots['missing']}' style='max-width:100%; margin-top:15px;'>"
        
        elif section_key == 'correlation':
            corr_info = result['analysis']['correlations']
            resultado_html += f"""
            <p><strong>{corr_info['count_strong']} correlações fortes</strong> detectadas (|r| > 0.7)</p>
            <div style='max-height:200px; overflow-y:auto; margin-top:10px;'>
                <table style='width:100%; border-collapse:collapse;'>
                    <thead><tr style='background:{color}10;'>
                        <th style='padding:8px; text-align:left; border-bottom:2px solid {color}30;'>Coluna 1</th>
                        <th style='padding:8px; text-align:left; border-bottom:2px solid {color}30;'>Coluna 2</th>
                        <th style='padding:8px; text-align:right; border-bottom:2px solid {color}30;'>Correlação</th>
                    </tr></thead>
                    <tbody>
            """
            for corr in corr_info['strong_correlations'][:8]:
                corr_color = "#D32F2F" if corr['correlation'] < -0.7 else "#388E3C"
                resultado_html += f"""
                    <tr style='border-bottom:1px solid #e0e0e0;'>
                        <td style='padding:8px;'>{corr['col1']}</td>
                        <td style='padding:8px;'>{corr['col2']}</td>
                        <td style='padding:8px; text-align:right; color:{corr_color};'>{corr['correlation']:.3f}</td>
                    </tr>
                """
            resultado_html += """
                    </tbody>
                </table>
            </div>
            """
            
            if 'correlation' in plots:
                resultado_html += f"<img src='{plots['correlation']}' style='max-width:100%; margin-top:15px;'>"
        
        elif section_key == 'outliers':
            outlier_info = result['analysis']['outliers']
            resultado_html += f"""
            <p><strong>{len(outlier_info['outlier_columns'])} colunas com outliers</strong> detectadas</p>
            <div style='max-height:200px; overflow-y:auto; margin-top:10px;'>
                <table style='width:100%; border-collapse:collapse;'>
                    <thead><tr style='background:{color}10;'>
                        <th style='padding:8px; text-align:left; border-bottom:2px solid {color}30;'>Coluna</th>
                        <th style='padding:8px; text-align:right; border-bottom:2px solid {color}30;'>Outliers</th>
                        <th style='padding:8px; text-align:right; border-bottom:2px solid {color}30;'>%</th>
                    </tr></thead>
                    <tbody>
            """
            for outlier in outlier_info['outlier_columns'][:8]:
                resultado_html += f"""
                    <tr style='border-bottom:1px solid #e0e0e0;'>
                        <td style='padding:8px;'>{outlier['column']}</td>
                        <td style='padding:8px; text-align:right;'>{outlier['outlier_count']:,}</td>
                        <td style='padding:8px; text-align:right;'>{outlier['percentage']:.1f}%</td>
                    </tr>
                """
            resultado_html += """
                    </tbody>
                </table>
            </div>
            """
        
        elif section_key == 'numeric':
            numeric_stats = result['analysis']['numeric_stats']
            resultado_html += f"""
            <p><strong>{len(numeric_stats)} colunas numéricas</strong> analisadas</p>
            <div style='max-height:200px; overflow-y:auto; margin-top:10px;'>
                <table style='width:100%; border-collapse:collapse;'>
                    <thead><tr style='background:{color}10;'>
                        <th style='padding:8px; text-align:left; border-bottom:2px solid {color}30;'>Coluna</th>
                        <th style='padding:8px; text-align:right; border-bottom:2px solid {color}30;'>Média</th>
                        <th style='padding:8px; text-align:right; border-bottom:2px solid {color}30;'>Desvio</th>
                        <th style='padding:8px; text-align:right; border-bottom:2px solid {color}30;'>Skewness</th>
                    </tr></thead>
                    <tbody>
            """
            for col, stats in list(numeric_stats.items())[:8]:
                skew_color = "#D32F2F" if abs(stats['skewness']) > 1 else "#388E3C"
                resultado_html += f"""
                    <tr style='border-bottom:1px solid #e0e0e0;'>
                        <td style='padding:8px;'>{col}</td>
                        <td style='padding:8px; text-align:right;'>{stats['mean']:.2f}</td>
                        <td style='padding:8px; text-align:right;'>{stats['std']:.2f}</td>
                        <td style='padding:8px; text-align:right; color:{skew_color};'>{stats['skewness']:.2f}</td>
                    </tr>
                """
            resultado_html += """
                    </tbody>
                </table>
            </div>
            """
            
            if 'distribution' in plots:
                resultado_html += f"<img src='{plots['distribution']}' style='max-width:100%; margin-top:15px;'>"
        
        elif section_key == 'categorical':
            categorical_stats = result['analysis']['categorical_stats']
            resultado_html += f"""
            <p><strong>{len(categorical_stats)} colunas categóricas</strong> analisadas</p>
            <div style='max-height:200px; overflow-y:auto; margin-top:10px;'>
                <table style='width:100%; border-collapse:collapse;'>
                    <thead><tr style='background:{color}10;'>
                        <th style='padding:8px; text-align:left; border-bottom:2px solid {color}30;'>Coluna</th>
                        <th style='padding:8px; text-align:right; border-bottom:2px solid {color}30;'>Únicos</th>
                        <th style='padding:8px; text-align:left; border-bottom:2px solid {color}30;'>Mais Comum</th>
                    </tr></thead>
                    <tbody>
            """
            for col, stats in list(categorical_stats.items())[:8]:
                resultado_html += f"""
                    <tr style='border-bottom:1px solid #e0e0e0;'>
                        <td style='padding:8px;'>{col}</td>
                        <td style='padding:8px; text-align:right;'>{stats['unique_values']:,}</td>
                        <td style='padding:8px;'>{stats['most_common'][:20]}{'...' if len(stats['most_common']) > 20 else ''}</td>
                    </tr>
                """
            resultado_html += """
                    </tbody>
                </table>
            </div>
            """
            
            if 'categorical' in plots:
                resultado_html += f"<img src='{plots['categorical']}' style='max-width:100%; margin-top:15px;'>"
        
        resultado_html += "</div>"
    
    # Amostra dos dados
    resultado_html += f"""
        <div style='background:#e8f5e9; border-radius:16px; padding:20px; margin-top:25px;'>
            <h3 style='color:#1b5e20; margin:0 0 15px 0; font-size:22px;'>📋 Amostra dos Dados</h3>
            {result['sample']}
        </div>
        
        <div style='background:#f5f5f5; border-radius:16px; padding:20px; margin-top:25px; text-align:center;'>
            <div style='font-weight:600; font-size:16px; color:#424242; margin-bottom:12px;'>
                ℹ️ Como funciona a análise
            </div>
            <div style='color:#616161; line-height:1.6; font-size:14px; max-width:650px; margin:0 auto;'>
                O DataProfiler analisa automaticamente datasets procurando por <strong>valores nulos</strong>, 
                <strong>correlações</strong>, <strong>outliers</strong>, <strong>distribuições</strong> e 
                <strong>padrões categóricos</strong>. Cada insight é apresentado com visualizações relevantes 
                e recomendações acionáveis para melhoria da qualidade dos dados.
            </div>
        </div>
    </div>
    """
    
    return resultado_html

def calculate_quality_score(stats, analysis):
    """Calcula score de qualidade do dataset"""
    score = 100
    
    # Penalizar valores nulos
    total_cells = stats['shape'][0] * stats['shape'][1]
    if total_cells > 0:
        missing_pct = (stats['missing_values'] / total_cells) * 100
        if missing_pct > 10:
            score -= missing_pct * 2
        elif missing_pct > 5:
            score -= missing_pct
    
    # Penalizar linhas duplicadas
    if stats['shape'][0] > 0:
        duplicate_pct = (stats['duplicate_rows'] / stats['shape'][0]) * 100
        if duplicate_pct > 5:
            score -= duplicate_pct * 3
        elif duplicate_pct > 1:
            score -= duplicate_pct * 2
    
    # Penalizar outliers excessivos
    if analysis['outliers']['has_outliers']:
        outlier_cols = len(analysis['outliers']['outlier_columns'])
        if outlier_cols > stats['numeric_columns'] * 0.5:
            score -= 15
        elif outlier_cols > 0:
            score -= 5
    
    # Ajustar score final
    score = max(0, min(100, score))
    
    if score >= 85:
        return "EXCELENTE"
    elif score >= 70:
        return "BOM"
    elif score >= 50:
        return "ACEITÁVEL"
    else:
        return "PROBLEMAS"

def get_quality_percentage(quality_score):
    """Retorna porcentagem para barra de qualidade"""
    percentages = {
        'EXCELENTE': 95,
        'BOM': 80,
        'ACEITÁVEL': 65,
        'PROBLEMAS': 40
    }
    return percentages.get(quality_score, 50)

# ============================================
# INTERFACE GRADIO
# ============================================

with gr.Blocks(theme=gr.themes.Soft(), title="DataProfiler - Analisador de Datasets") as demo:
    gr.Markdown("""
    <div style='text-align:center; max-width:800px; margin:0 auto 30px auto; padding:0 15px;'>
        <div style='background:linear-gradient(135deg, #e8f5e9, #c8e6c9); border-radius:24px; padding:30px; box-shadow:0 6px 20px rgba(46,125,50,0.15);'>
            <h1 style='font-size:42px; font-weight:800; margin:0 0 15px 0; color:#1b5e20; line-height:1.15;'>📊 DataProfiler</h1>
            <p style='font-size:19px; color:#2e7d32; line-height:1.6; max-width:650px; margin:0 auto; font-weight:400;'>
                Analisador automático de datasets com relatórios estatísticos e visualizações inteligentes
            </p>
            <div style='background:#c8e6c9; border-radius:14px; padding:15px; margin-top:20px; display:inline-block;'>
                <p style='margin:0; color:#1b5e20; font-size:16px; font-weight:600;'>
                    ✅ 100% CPU • ✅ Suporte CSV/Excel • ✅ Relatórios automáticos
                </p>
            </div>
        </div>
    </div>
    """)
    
    with gr.Row(equal_height=False):
        with gr.Column(scale=1, min_width=450):
            gr.Markdown("### 📁 Upload seu Dataset")
            file_input = gr.File(
                label="Upload CSV ou Excel",
                file_types=[".csv", ".xlsx", ".xls"],
                type="filepath"
            )
            
            with gr.Row():
                analyze_btn = gr.Button(
                    "🔍 Analisar Dataset",
                    variant="primary",
                    size="lg"
                )
                clear_btn = gr.Button("🗑️ Limpar", size="lg")
            
            gr.Markdown("""
            <div style='background:#e8f5e9; border-radius:14px; padding:18px; margin-top:25px; font-size:14px; line-height:1.6;'>
                <p style='margin:0 0 12px 0; font-weight:600; color:#1b5e20; font-size:15px;'>ℹ️ Instruções:</p>
                <p style='margin:0 0 8px 0;'>• Suporta arquivos CSV e Excel (.xlsx, .xls)</p>
                <p style='margin:0 0 8px 0;'>• Dataset deve ter pelo menos 10 linhas</p>
                <p style='margin:0 0 8px 0;'>• Análise automática de qualidade, correlações e outliers</p>
                <p style='margin:12px 0 0 0; color:#d32f2f; font-weight:500; background:#ffcdd2; padding:10px; border-radius:10px;'>
                    ⚠️ Arquivos muito grandes podem causar timeout no HF Spaces
                </p>
            </div>
            """)
        
        with gr.Column(scale=1, min_width=500):
            gr.Markdown("### 🎯 Resultado da Análise")
            result_output = gr.HTML(
                value="<div style='text-align:center; padding:50px 30px; color:#78909c; min-height:500px; background:#fafbfc; border-radius:18px;'><p style='font-size:24px; margin-bottom:20px; font-weight:600; color:#455a64;'>Aguardando dataset para análise...</p><p style='font-size:16px; opacity:0.85; max-width:600px; margin:0 auto; line-height:1.6;'>Faça upload de um arquivo CSV ou Excel para que o DataProfiler gere relatórios estatísticos automáticos com visualizações inteligentes.</p></div>"
            )
    
    # Funções de botão
    analyze_btn.click(
        profile_dataset,
        inputs=[file_input],
        outputs=[result_output]
    )
    
    def clear_inputs():
        return None, "<div style='text-align:center; padding:50px 30px; color:#78909c; min-height:500px; background:#fafbfc; border-radius:18px;'><p style='font-size:24px; margin-bottom:20px; font-weight:600; color:#455a64;'>Aguardando dataset para análise...</p><p style='font-size:16px; opacity:0.85; max-width:600px; margin:0 auto; line-height:1.6;'>Faça upload de um arquivo CSV ou Excel para que o DataProfiler gere relatórios estatísticos automáticos com visualizações inteligentes.</p></div>"
    
    clear_btn.click(
        clear_inputs,
        inputs=[],
        outputs=[file_input, result_output]
    )

# Rodapé
gr.Markdown("""
<div style='text-align:center; margin-top:40px; padding:25px; color:#546e7a; font-size:14px; line-height:1.7; max-width:800px; margin-left:auto; margin-right:auto; border-top:1px solid #e0e0e0; background:#fafafa; border-radius:14px;'>
    <p style='margin:8px 0; font-weight:700; color:#1b5e20; font-size:16px;'>DataProfiler v3.0 • Analisador Automático de Datasets</p>
    
    <div style='display:flex; justify-content:center; gap:30px; flex-wrap:wrap; margin:20px 0; max-width:700px; margin-left:auto; margin-right:auto; font-size:13px;'>
        <div style='text-align:left; max-width:220px;'>
            <p style='font-weight:600; color:#1b5e20; margin:6px 0;'>📊 Análises</p>
            <p style='margin:4px 0; line-height:1.5;'>• Qualidade do dataset<br>• Valores nulos<br>• Correlações<br>• Outliers<br>• Distribuições</p>
        </div>
        <div style='text-align:left; max-width:220px;'>
            <p style='font-weight:600; color:#1b5e20; margin:6px 0;'>📈 Visualizações</p>
            <p style='margin:4px 0; line-height:1.5;'>• Heatmaps de correlação<br>• Gráficos de distribuição<br>• Análise categórica<br>• Padrões de missing data</p>
        </div>
        <div style='text-align:left; max-width:220px;'>
            <p style='font-weight:600; color:#1b5e20; margin:6px 0;'>💼 Aplicações</p>
            <p style='margin:4px 0; line-height:1.5;'>• Exploração de dados<br>• Preparação de datasets<br>• Detecção de problemas<br>• Engenharia de features</p>
        </div>
    </div>
    
    <p style='margin:15px 0 0 0; padding-top:15px; border-top:1px dashed #bdbdbd; font-style:italic; color:#455a64; font-size:13px;'>
        ✨ Sistema de análise de dados automático — diferencial competitivo para vagas de Engenheiro de Dados/ML
    </p>
</div>
""")

if __name__ == "__main__":
    demo.launch()
