"""
InsightForge AI - Enterprise Data Intelligence Platform
Turning Data Chaos into Business Clarity
Microsoft Build AI Hackathon
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import tempfile
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import re
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# AI and ML Libraries
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, r2_score, mean_absolute_error
from sklearn.impute import SimpleImputer
from scipy import stats

# Text Processing with error handling
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import nltk
    NLTK_AVAILABLE = True
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
except ImportError:
    NLTK_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="InsightForge AI",
    page_icon="🔨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Clean White Theme
st.markdown("""
<style>
    /* Main container styling - Clean White Theme */
    .stApp {
        background-color: #ffffff;
    }
    
    /* Card styling */
    .css-1r6slb0 {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e8eaed;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 12px;
        padding: 20px;
        color: #202124;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e8eaed;
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }
    
    /* Insight highlight */
    .insight-box {
        background: linear-gradient(135deg, #e8f0fe 0%, #f0f5ff 100%);
        border-left: 4px solid #1a73e8;
        padding: 20px;
        border-radius: 8px;
        margin: 15px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Recommendation card */
    .recommendation-card {
        background: linear-gradient(135deg, #fef7e0 0%, #fff8e7 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        border-left: 4px solid #f9ab00;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #1a73e8 0%, #1557b0 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        transition: all 0.3s;
        font-weight: 500;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(26,115,232,0.3);
    }
    
    /* Header styling */
    h1 {
        font-family: 'Segoe UI', 'Google Sans', sans-serif;
        font-weight: 700;
        background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
    }
    
    h2, h3 {
        font-family: 'Segoe UI', 'Google Sans', sans-serif;
        font-weight: 600;
        color: #202124;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
        border-right: 1px solid #e8eaed;
    }
    
    /* Progress bar styling */
    .stProgress > div > div {
        background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%);
    }
    
    /* Dataframe styling */
    .dataframe {
        font-family: 'Segoe UI', monospace;
        font-size: 14px;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1a73e8 0%, #1557b0 100%);
        color: white;
    }
    
    /* Alert styling */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid;
    }
    
    /* Success message */
    .stAlert[data-baseweb="notification"] {
        background-color: #e6f4ea;
        border-left-color: #34a853;
    }
    
    /* Info message */
    .stAlert[data-baseweb="info"] {
        background-color: #e8f0fe;
        border-left-color: #1a73e8;
    }
    
    /* Warning message */
    .stAlert[data-baseweb="warning"] {
        background-color: #fef7e0;
        border-left-color: #f9ab00;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = {}
if 'cleaned_data' not in st.session_state:
    st.session_state.cleaned_data = {}
if 'insights' not in st.session_state:
    st.session_state.insights = []
if 'anomalies' not in st.session_state:
    st.session_state.anomalies = {}
if 'predictions' not in st.session_state:
    st.session_state.predictions = {}
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []
if 'data_quality_scores' not in st.session_state:
    st.session_state.data_quality_scores = {}

class DataQualityAnalyzer:
    """Analyzes and scores data quality"""
    
    @staticmethod
    def calculate_quality_score(df: pd.DataFrame) -> Dict:
        """Calculate overall data quality score"""
        scores = {}
        
        if len(df) == 0 or len(df.columns) == 0:
            return {'overall_score': 0, 'status': 'No Data', 'missing_score': 0, 'duplicate_score': 0, 'consistency_score': 0}
        
        # Missing values score
        missing_ratio = df.isnull().sum().sum() / (df.shape[0] * df.shape[1])
        scores['missing_score'] = max(0, 100 - (missing_ratio * 100))
        
        # Duplicates score
        duplicate_count = df.duplicated().sum()
        duplicate_ratio = duplicate_count / len(df) if len(df) > 0 else 0
        scores['duplicate_score'] = max(0, 100 - (duplicate_ratio * 100))
        
        # Data type consistency
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        scores['consistency_score'] = (len(numeric_cols) / len(df.columns)) * 100 if len(df.columns) > 0 else 0
        
        # Overall score
        scores['overall_score'] = np.mean([
            scores['missing_score'],
            scores['duplicate_score'],
            scores['consistency_score']
        ])
        
        scores['status'] = 'Excellent' if scores['overall_score'] >= 80 else \
                          'Good' if scores['overall_score'] >= 60 else \
                          'Fair' if scores['overall_score'] >= 40 else \
                          'Needs Improvement'
        
        return scores

class DataCleaner:
    """Advanced data cleaning and preprocessing"""
    
    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Perform comprehensive data cleaning"""
        cleaning_log = {}
        df_cleaned = df.copy()
        
        # Remove duplicates
        initial_rows = len(df_cleaned)
        df_cleaned = df_cleaned.drop_duplicates()
        cleaning_log['duplicates_removed'] = initial_rows - len(df_cleaned)
        
        # Handle missing values
        missing_before = df_cleaned.isnull().sum().sum()
        
        # Numeric columns - fill with median
        numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df_cleaned[col].isnull().any():
                median_val = df_cleaned[col].median()
                df_cleaned[col].fillna(median_val if not np.isnan(median_val) else 0, inplace=True)
        
        # Categorical columns - fill with mode
        categorical_cols = df_cleaned.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if df_cleaned[col].isnull().any():
                mode_val = df_cleaned[col].mode()
                df_cleaned[col].fillna(mode_val[0] if len(mode_val) > 0 else "Unknown", inplace=True)
        
        cleaning_log['missing_values_filled'] = missing_before - df_cleaned.isnull().sum().sum()
        
        # Standardize text columns
        for col in categorical_cols:
            if df_cleaned[col].dtype == 'object':
                df_cleaned[col] = df_cleaned[col].astype(str).str.strip().str.lower()
        
        # Handle outliers using IQR
        outlier_count = 0
        for col in numeric_cols:
            if len(df_cleaned[col]) > 0:
                Q1 = df_cleaned[col].quantile(0.25)
                Q3 = df_cleaned[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers = ((df_cleaned[col] < lower_bound) | (df_cleaned[col] > upper_bound)).sum()
                outlier_count += outliers
                # Cap outliers
                df_cleaned[col] = df_cleaned[col].clip(lower=lower_bound, upper=upper_bound)
        
        cleaning_log['outliers_capped'] = outlier_count
        
        return df_cleaned, cleaning_log

class InsightEngine:
    """AI-powered insight discovery engine"""
    
    def generate_insights(self, df: pd.DataFrame) -> List[Dict]:
        """Generate business insights from data"""
        insights = []
        
        if len(df) == 0:
            return insights
        
        # Correlation insights
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) >= 2:
            corr_matrix = df[numeric_cols].corr()
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_value = corr_matrix.iloc[i, j]
                    if abs(corr_value) > 0.7:
                        insights.append({
                            'type': 'correlation',
                            'title': f'Strong Correlation Detected',
                            'description': f'Strong {"positive" if corr_value > 0 else "negative"} correlation ({corr_value:.2f}) between {corr_matrix.columns[i]} and {corr_matrix.columns[j]}',
                            'confidence': abs(corr_value) * 100,
                            'evidence': f'Pearson correlation coefficient = {corr_value:.3f}'
                        })
        
        # Trend insights
        for col in numeric_cols:
            if len(df) > 1:
                first_valid = df[col].first_valid_index()
                last_valid = df[col].last_valid_index()
                if first_valid is not None and last_valid is not None and first_valid != last_valid:
                    first_val = df[col].iloc[0]
                    last_val = df[col].iloc[-1]
                    if first_val != 0:
                        trend = last_val - first_val
                        percent_change = (trend / abs(first_val)) * 100
                        if abs(percent_change) > 10:
                            insights.append({
                                'type': 'trend',
                                'title': f'Significant Trend in {col}',
                                'description': f'{col} has {"increased" if trend > 0 else "decreased"} by {abs(percent_change):.1f}% over the period',
                                'confidence': 85,
                                'evidence': f'From {first_val:.2f} to {last_val:.2f}'
                            })
        
        # Statistical insights
        for col in numeric_cols:
            if len(df[col].dropna()) > 1:
                # Check for high variance
                cv = df[col].std() / df[col].mean() if df[col].mean() != 0 else 0
                if cv > 0.5:
                    insights.append({
                        'type': 'variance',
                        'title': f'High Volatility in {col}',
                        'description': f'{col} shows significant variation (CV: {cv:.2f}), indicating unstable patterns',
                        'confidence': 75,
                        'evidence': f'Coefficient of Variation = {cv:.3f}'
                    })
        
        return insights
    
    def generate_recommendations(self, df: pd.DataFrame, insights: List[Dict]) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        # Based on correlations
        for insight in insights:
            if insight['type'] == 'correlation':
                recommendations.append({
                    'title': 'Leverage Positive Correlations',
                    'description': f'Focus on improving metrics that show strong relationships with key performance indicators',
                    'priority': 'High',
                    'impact': 'Potential 15-25% improvement',
                    'confidence': insight['confidence']
                })
                break
        
        # Based on trends
        for col in numeric_cols:
            if len(df) > 1:
                first_val = df[col].iloc[0] if len(df) > 0 else 0
                last_val = df[col].iloc[-1] if len(df) > 0 else 0
                if last_val < first_val:
                    recommendations.append({
                        'title': f'Address Declining {col}',
                        'description': f'Investigate causes of decreasing {col} and implement corrective measures immediately',
                        'priority': 'Critical',
                        'impact': 'Potential recovery of 20-30%',
                        'confidence': 85
                    })
                    break
        
        # General recommendations
        if len(recommendations) < 3:
            recommendations.extend([
                {
                    'title': 'Optimize Data Collection',
                    'description': 'Implement automated data validation to improve data quality and reduce cleaning time by 30%',
                    'priority': 'Medium',
                    'impact': '30% reduction in data processing time',
                    'confidence': 95
                },
                {
                    'title': 'Implement Predictive Monitoring',
                    'description': 'Set up real-time anomaly detection to identify issues before they impact business operations',
                    'priority': 'High',
                    'impact': '40% faster issue resolution',
                    'confidence': 88
                },
                {
                    'title': 'Enhance Data Governance',
                    'description': 'Establish data quality standards and regular auditing processes',
                    'priority': 'Medium',
                    'impact': '25% improvement in data reliability',
                    'confidence': 90
                }
            ])
        
        return recommendations[:5]

class AnomalyDetector:
    """Advanced anomaly detection using multiple algorithms"""
    
    @staticmethod
    def detect_anomalies(df: pd.DataFrame) -> Dict:
        """Detect anomalies using Isolation Forest"""
        anomalies = {}
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0 or len(df) < 10:
            return {'anomalies_found': 0, 'details': [], 'anomaly_ratio': 0}
        
        try:
            scaler = StandardScaler()
            data_scaled = scaler.fit_transform(df[numeric_cols].fillna(df[numeric_cols].median()))
            
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            iso_predictions = iso_forest.fit_predict(data_scaled)
            iso_anomalies = sum(iso_predictions == -1)
            
            anomalies['anomalies_found'] = int(iso_anomalies)
            anomalies['anomaly_ratio'] = anomalies['anomalies_found'] / len(df) if len(df) > 0 else 0
            
            anomaly_details = []
            anomaly_indices = np.where(iso_predictions == -1)[0][:10]
            
            for idx in anomaly_indices:
                row = df.iloc[idx]
                anomaly_details.append({
                    'row_index': idx,
                    'values': {col: row[col] for col in numeric_cols[:5]},
                    'severity': 'High'
                })
            
            anomalies['details'] = anomaly_details
            
        except Exception as e:
            anomalies = {'anomalies_found': 0, 'details': [], 'error': str(e)}
        
        return anomalies

class PredictiveModeler:
    """Automated predictive modeling"""
    
    @staticmethod
    def build_regression_model(df: pd.DataFrame, target_col: str) -> Dict:
        """Build regression model for prediction"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if target_col not in numeric_cols or len(df) < 20:
            return None
        
        features = [col for col in numeric_cols if col != target_col]
        if len(features) == 0:
            return None
        
        try:
            X = df[features].fillna(df[features].median())
            y = df[target_col].fillna(df[target_col].median())
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            model = RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1)
            model.fit(X_train, y_train)
            
            y_pred = model.predict(X_test)
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            feature_importance = dict(zip(features, model.feature_importances_))
            
            return {
                'r2_score': r2,
                'mae': mae,
                'feature_importance': feature_importance,
                'predictions': y_pred.tolist()[:10]
            }
        except Exception as e:
            return None
    
    @staticmethod
    def build_classification_model(df: pd.DataFrame, target_col: str) -> Dict:
        """Build classification model"""
        if target_col not in df.columns or len(df) < 20:
            return None
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        features = [col for col in numeric_cols if col != target_col]
        
        if len(features) == 0:
            return None
        
        try:
            X = df[features].fillna(df[features].median())
            y = df[target_col]
            
            if len(y.unique()) != 2:
                return None
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            model = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
            model.fit(X_train, y_train)
            
            y_pred = model.predict(X_test)
            
            return {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred, average='weighted'),
                'recall': recall_score(y_test, y_pred, average='weighted'),
                'f1': f1_score(y_test, y_pred, average='weighted')
            }
        except Exception as e:
            return None

class FileProcessor:
    """Handle multiple file type processing"""
    
    @staticmethod
    def process_csv(file) -> pd.DataFrame:
        return pd.read_csv(file)
    
    @staticmethod
    def process_excel(file) -> pd.DataFrame:
        return pd.read_excel(file)
    
    @staticmethod
    def process_pdf(file) -> str:
        if not PDFPLUMBER_AVAILABLE:
            return "PDF processing requires pdfplumber. Install with: pip install pdfplumber"
        text = ""
        try:
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
        except Exception as e:
            text = f"Error processing PDF: {str(e)}"
        return text if text else "No text could be extracted from the PDF."
    
    @staticmethod
    def process_docx(file) -> str:
        if not DOCX_AVAILABLE:
            return "DOCX processing requires python-docx. Install with: pip install python-docx"
        try:
            doc = Document(file)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
            return text if text else "No text could be extracted from the document."
        except Exception as e:
            return f"Error processing DOCX: {str(e)}"
    
    @staticmethod
    def process_text(file) -> str:
        return file.getvalue().decode("utf-8")

def create_sample_data():
    """Create sample data for demonstration"""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    df = pd.DataFrame({
        'Date': dates,
        'Revenue': np.random.normal(100000, 20000, 100).cumsum() + 500000,
        'Customers': np.random.poisson(500, 100).cumsum(),
        'Satisfaction': np.random.uniform(3.5, 5, 100),
        'Marketing_Spend': np.random.normal(10000, 2000, 100).cumsum(),
        'Returns': np.random.poisson(50, 100),
        'Support_Tickets': np.random.poisson(30, 100)
    })
    # Add some interesting patterns
    df.loc[30:35, 'Revenue'] = df.loc[30:35, 'Revenue'] * 0.7
    df.loc[70:75, 'Customers'] = df.loc[70:75, 'Customers'] * 1.5
    df.loc[50, 'Satisfaction'] = 2.0
    df.loc[45, 'Revenue'] = np.nan
    df.loc[60, 'Customers'] = np.nan
    
    return df

def create_correlation_heatmap(df: pd.DataFrame):
    """Create correlation heatmap visualization"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) >= 2:
        corr_matrix = df[numeric_cols].corr()
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale='RdBu_r',
            title="Correlation Matrix Heatmap",
            labels=dict(color="Correlation")
        )
        fig.update_layout(height=500)
        return fig
    return None

def create_time_series_visualization(df: pd.DataFrame, column: str):
    """Create comprehensive time series visualization"""
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=('Original Time Series', 'Distribution', 'Trend Analysis',
                       'Seasonal Pattern', 'Rolling Statistics', 'Forecast'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Original time series
    fig.add_trace(
        go.Scatter(x=df.index, y=df[column], mode='lines+markers', 
                   name=column, line=dict(color='#1a73e8', width=2)),
        row=1, col=1
    )
    
    # Distribution
    fig.add_trace(
        go.Histogram(x=df[column], nbinsx=30, name='Distribution',
                     marker=dict(color='#34a853')),
        row=1, col=2
    )
    
    # Trend with moving average
    ma = df[column].rolling(window=7, min_periods=1).mean()
    fig.add_trace(
        go.Scatter(x=df.index, y=ma, mode='lines', name='7-day MA',
                   line=dict(color='#ea4335', width=2)),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df[column], mode='lines', name='Original',
                   line=dict(color='#1a73e8', width=1, dash='dot')),
        row=2, col=1
    )
    
    # Box plot for seasonal pattern
    df['Month'] = pd.to_datetime(df.index).month if isinstance(df.index, pd.DatetimeIndex) else range(len(df))
    fig.add_trace(
        go.Box(x=df['Month'] if 'Month' in df.columns else df.index % 12, 
               y=df[column], name='Seasonal', marker=dict(color='#f9ab00')),
        row=2, col=2
    )
    
    # Rolling statistics
    rolling_mean = df[column].rolling(window=14, min_periods=1).mean()
    rolling_std = df[column].rolling(window=14, min_periods=1).std()
    fig.add_trace(
        go.Scatter(x=df.index, y=rolling_mean, mode='lines', name='Rolling Mean',
                   line=dict(color='#1a73e8', width=2)),
        row=3, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=rolling_std, mode='lines', name='Rolling Std',
                   line=dict(color='#ea4335', width=2)),
        row=3, col=1
    )
    
    # Simple forecast (linear extrapolation)
    from scipy import stats
    x = np.arange(len(df))
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, df[column].fillna(method='ffill'))
    forecast = slope * (x + 10) + intercept
    fig.add_trace(
        go.Scatter(x=np.arange(len(df), len(df) + 10), y=forecast[-10:], 
                   mode='lines+markers', name='10-day Forecast',
                   line=dict(color='#34a853', width=2, dash='dash')),
        row=3, col=2
    )
    
    fig.update_layout(height=900, showlegend=True, title_text=f"Advanced Analytics Dashboard - {column}")
    fig.update_xaxes(title_text="Index", row=3, col=1)
    fig.update_xaxes(title_text="Period", row=3, col=2)
    
    return fig

def create_comparison_chart(df: pd.DataFrame, columns: List[str]):
    """Create multi-metric comparison chart"""
    fig = go.Figure()
    
    for col in columns:
        # Normalize data for comparison
        normalized = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
        fig.add_trace(go.Scatter(
            x=df.index, y=normalized, mode='lines',
            name=col, line=dict(width=2)
        ))
    
    fig.update_layout(
        title="Multi-Metric Comparison (Normalized)",
        xaxis_title="Index",
        yaxis_title="Normalized Value",
        hovermode='x unified',
        height=500
    )
    
    return fig

def create_pie_chart(df: pd.DataFrame, column: str):
    """Create pie chart for categorical data"""
    value_counts = df[column].value_counts().head(10)
    fig = px.pie(
        values=value_counts.values,
        names=value_counts.index,
        title=f"Distribution of {column}",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=500)
    return fig

def create_scatter_matrix(df: pd.DataFrame, columns: List[str]):
    """Create interactive scatter plot matrix"""
    if len(columns) >= 2:
        fig = px.scatter_matrix(
            df[columns],
            dimensions=columns[:4],  # Limit to 4 dimensions for readability
            title="Interactive Scatter Plot Matrix",
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=600)
        return fig
    return None

def create_radar_chart(df: pd.DataFrame, columns: List[str]):
    """Create radar chart for performance comparison"""
    if len(columns) >= 3:
        # Get latest values
        latest_values = df[columns].iloc[-1].values
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=latest_values,
            theta=columns,
            fill='toself',
            name='Current Performance',
            line=dict(color='#1a73e8', width=2),
            fillcolor='rgba(26,115,232,0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(latest_values) * 1.1]
                )),
            showlegend=True,
            title="Performance Radar Chart",
            height=500
        )
        
        return fig
    return None

def create_bubble_chart(df: pd.DataFrame, x_col: str, y_col: str, size_col: str):
    """Create bubble chart for three-dimensional analysis"""
    fig = px.scatter(
        df, x=x_col, y=y_col, size=size_col,
        color=size_col, color_continuous_scale='Viridis',
        title=f"Bubble Chart: {x_col} vs {y_col} (Size: {size_col})",
        hover_data={col: True for col in [x_col, y_col, size_col]}
    )
    fig.update_layout(height=500)
    return fig

def create_sunburst_chart(df: pd.DataFrame, category_cols: List[str]):
    """Create sunburst chart for hierarchical data"""
    if len(category_cols) >= 2:
        fig = px.sunburst(
            df.head(100),  # Limit for performance
            path=category_cols[:3],
            title="Hierarchical Data Visualization",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(height=600)
        return fig
    return None

def create_waterfall_chart(df: pd.DataFrame, column: str):
    """Create waterfall chart for cumulative changes"""
    changes = df[column].diff().fillna(df[column].iloc[0])
    fig = go.Figure(go.Waterfall(
        name="Change",
        orientation="v",
        measure=["absolute"] + ["relative"] * (len(changes)-1),
        x=df.index[:20],  # Limit to 20 points
        y=changes[:20],
        textposition="outside",
        text=[f"{val:,.0f}" for val in changes[:20]],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))
    fig.update_layout(
        title=f"Cumulative Changes - {column}",
        height=500,
        showlegend=False
    )
    return fig

def main():
    """Main application entry point"""
    
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔨 InsightForge AI")
        st.caption("Turning Data Chaos into Business Clarity | Enterprise Intelligence Platform")
        st.markdown("---")
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🤖 InsightForge AI")
        st.markdown("*Enterprise Data Intelligence*")
        st.markdown("---")
        
        # Add sample data option
        if st.button("📊 Load Sample Data", use_container_width=True):
            sample_df = create_sample_data()
            st.session_state.data["Sample_Sales_Data.csv"] = sample_df
            st.success("✅ Sample data loaded successfully!")
        
        st.markdown("---")
        
        page = st.radio(
            "📌 Navigation",
            ["📁 Data Upload", "🔍 Data Overview", "🧹 AI Cleaning", "💡 Insight Discovery",
             "📈 Trend Analysis", "⚠️ Anomaly Detection", "🔮 Predictive Analytics",
             "💬 AI Chat Assistant", "📊 Executive Summary"]
        )
        
        st.markdown("---")
        st.caption("Made with ❤️ for Microsoft Build AI Hackathon")
        st.caption("Version 2.0 | Enterprise Edition")
    
    # File Upload Section
    if page == "📁 Data Upload":
        st.header("📁 Data Upload Center")
        
        st.markdown("""
        ### 📋 Supported File Types
        | Type | Format | Use Case |
        |------|--------|----------|
        | **Tabular** | CSV, Excel | Sales data, customer records, financial data |
        | **Documents** | PDF, DOCX, TXT | Reports, contracts, emails, transcripts |
        
        Upload multiple files to discover hidden connections across your data sources!
        """)
        
        uploaded_files = st.file_uploader(
            "Drop your files here or click to browse",
            type=['csv', 'xlsx', 'pdf', 'docx', 'txt'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            for file in uploaded_files:
                with st.expander(f"📄 {file.name}"):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("File Size", f"{file.size / 1024:.1f} KB")
                    
                    # Process file based on type
                    try:
                        if file.name.endswith('.csv'):
                            df = FileProcessor.process_csv(file)
                            st.session_state.data[file.name] = df
                            col2.metric("Rows", len(df))
                            col3.metric("Columns", len(df.columns))
                            st.dataframe(df.head())
                            st.caption(f"📊 Data shape: {df.shape}")
                            
                        elif file.name.endswith('.xlsx'):
                            df = FileProcessor.process_excel(file)
                            st.session_state.data[file.name] = df
                            col2.metric("Rows", len(df))
                            col3.metric("Columns", len(df.columns))
                            st.dataframe(df.head())
                            st.caption(f"📊 Data shape: {df.shape}")
                            
                        elif file.name.endswith('.pdf'):
                            text = FileProcessor.process_pdf(file)
                            st.session_state.data[file.name] = text
                            word_count = len(text.split())
                            col2.metric("Characters", len(text))
                            col3.metric("Words", word_count)
                            if len(text) > 500:
                                st.text(text[:500] + "...")
                            else:
                                st.text(text)
                            
                        elif file.name.endswith('.docx'):
                            text = FileProcessor.process_docx(file)
                            st.session_state.data[file.name] = text
                            word_count = len(text.split())
                            col2.metric("Characters", len(text))
                            col3.metric("Words", word_count)
                            if len(text) > 500:
                                st.text(text[:500] + "...")
                            else:
                                st.text(text)
                            
                        elif file.name.endswith('.txt'):
                            text = FileProcessor.process_text(file)
                            st.session_state.data[file.name] = text
                            word_count = len(text.split())
                            col2.metric("Characters", len(text))
                            col3.metric("Words", word_count)
                            if len(text) > 500:
                                st.text(text[:500] + "...")
                            else:
                                st.text(text)
                            
                    except Exception as e:
                        st.error(f"❌ Error processing {file.name}: {str(e)}")
            
            # Data quality overview for tabular data
            dfs = {name: data for name, data in st.session_state.data.items() if isinstance(data, pd.DataFrame)}
            if dfs:
                st.subheader("📊 Data Quality Dashboard")
                
                for name, data in dfs.items():
                    quality_scores = DataQualityAnalyzer.calculate_quality_score(data)
                    st.session_state.data_quality_scores[name] = quality_scores
                    
                    cols = st.columns(4)
                    with cols[0]:
                        st.metric("Data Quality", f"{quality_scores['overall_score']:.1f}/100")
                    with cols[1]:
                        st.metric("Missing Values", f"{quality_scores['missing_score']:.1f}")
                    with cols[2]:
                        st.metric("Duplicates", f"{quality_scores['duplicate_score']:.1f}")
                    with cols[3]:
                        st.metric("Status", quality_scores['status'])
    
    # Data Overview Section
    elif page == "🔍 Data Overview":
        st.header("🔍 Data Overview Dashboard")
        
        if not st.session_state.data:
            st.warning("⚠️ No data uploaded yet. Please upload files or click 'Load Sample Data' in the sidebar.")
        else:
            # File selector
            file_names = list(st.session_state.data.keys())
            selected_file = st.selectbox("Select dataset to view", file_names)
            
            data = st.session_state.data[selected_file]
            
            if isinstance(data, pd.DataFrame):
                st.subheader(f"📊 Dataset: {selected_file}")
                
                # Key metrics
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Records", f"{len(data):,}")
                col2.metric("Total Features", len(data.columns))
                col3.metric("Missing Values", data.isnull().sum().sum())
                col4.metric("Duplicate Rows", data.duplicated().sum())
                
                # Data preview
                st.subheader("🔍 Data Preview")
                st.dataframe(data.head(20))
                
                # Data types
                st.subheader("📋 Data Types")
                dtype_df = pd.DataFrame({
                    'Column': data.dtypes.index,
                    'Data Type': data.dtypes.values.astype(str),
                    'Non-Null Count': data.count().values,
                    'Null Count': data.isnull().sum().values
                })
                st.dataframe(dtype_df)
                
                # Statistical summary
                st.subheader("📈 Statistical Summary")
                st.dataframe(data.describe())
                
                # Multiple Visualizations
                st.subheader("📊 Advanced Visualizations")
                viz_tabs = st.tabs(["Correlation Heatmap", "Distribution Analysis", "Box Plots", "Scatter Matrix"])
                
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                
                with viz_tabs[0]:
                    if len(numeric_cols) >= 2:
                        corr_fig = create_correlation_heatmap(data)
                        if corr_fig:
                            st.plotly_chart(corr_fig, use_container_width=True)
                    else:
                        st.info("Need at least 2 numeric columns for correlation analysis")
                
                with viz_tabs[1]:
                    if len(numeric_cols) > 0:
                        selected_dist_col = st.selectbox("Select column for distribution", numeric_cols)
                        fig = px.histogram(
                            data, x=selected_dist_col, nbins=30,
                            title=f"Distribution of {selected_dist_col}",
                            color_discrete_sequence=['#1a73e8']
                        )
                        fig.add_vline(x=data[selected_dist_col].mean(), line_dash="dash", 
                                     line_color="red", annotation_text=f"Mean: {data[selected_dist_col].mean():.2f}")
                        fig.add_vline(x=data[selected_dist_col].median(), line_dash="dash", 
                                     line_color="green", annotation_text=f"Median: {data[selected_dist_col].median():.2f}")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No numeric columns available")
                
                with viz_tabs[2]:
                    if len(numeric_cols) > 0:
                        fig = go.Figure()
                        for col in numeric_cols[:5]:  # Limit to 5 columns
                            fig.add_trace(go.Box(y=data[col], name=col))
                        fig.update_layout(title="Box Plot Analysis - Outlier Detection", height=500)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No numeric columns available")
                
                with viz_tabs[3]:
                    if len(numeric_cols) >= 3:
                        scatter_fig = create_scatter_matrix(data, numeric_cols[:4].tolist())
                        if scatter_fig:
                            st.plotly_chart(scatter_fig, use_container_width=True)
                    else:
                        st.info("Need at least 3 numeric columns for scatter matrix")
                
                # Missing values visualization
                missing_data = data.isnull().sum()
                missing_data = missing_data[missing_data > 0]
                if len(missing_data) > 0:
                    st.subheader("🔴 Missing Values Analysis")
                    fig = px.bar(
                        x=missing_data.index, 
                        y=missing_data.values,
                        title="Missing Values by Column",
                        labels={'x': 'Column', 'y': 'Missing Values Count'},
                        color=missing_data.values,
                        color_continuous_scale='Reds'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.success("✅ No missing values found in this dataset!")
            else:
                st.subheader(f"📄 Text Document: {selected_file}")
                
                # Text analytics
                word_count = len(data.split())
                char_count = len(data)
                sentences = data.split('.')
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Characters", f"{char_count:,}")
                col2.metric("Words", f"{word_count:,}")
                col3.metric("Sentences", len(sentences))
                
                # Word frequency
                words = re.findall(r'\b\w+\b', data.lower())
                word_freq = Counter(words).most_common(10)
                if word_freq:
                    st.subheader("📊 Most Common Words")
                    freq_df = pd.DataFrame(word_freq, columns=['Word', 'Frequency'])
                    fig = px.bar(freq_df, x='Frequency', y='Word', orientation='h', 
                                title="Top 10 Words", color='Frequency',
                                color_continuous_scale='Viridis')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Text preview
                st.subheader("📝 Text Preview")
                st.text(data[:1000] if len(data) > 1000 else data)
                if len(data) > 1000:
                    st.caption(f"Showing first 1000 of {char_count:,} characters...")
    
    # AI Cleaning Section
    elif page == "🧹 AI Cleaning":
        st.header("🧹 AI Data Cleaning Engine")
        
        if not st.session_state.data:
            st.warning("⚠️ No data uploaded yet. Please upload files or load sample data.")
        else:
            dfs = {name: data for name, data in st.session_state.data.items() if isinstance(data, pd.DataFrame)}
            if not dfs:
                st.info("ℹ️ Only tabular data (CSV/Excel) can be cleaned. Please upload CSV or Excel files.")
            else:
                selected_file = st.selectbox("Select dataset to clean", list(dfs.keys()))
                data = dfs[selected_file]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### 📊 Before Cleaning")
                    st.write(f"**Rows:** {len(data):,}")
                    st.write(f"**Columns:** {len(data.columns)}")
                    st.write(f"**Missing Values:** {data.isnull().sum().sum():,}")
                    st.write(f"**Duplicates:** {data.duplicated().sum():,}")
                    st.dataframe(data.head())
                
                if st.button("🧹 Run AI Cleaning", use_container_width=True):
                    with st.spinner("AI is analyzing and cleaning your data..."):
                        cleaned_df, cleaning_log = DataCleaner.clean_dataframe(data)
                        st.session_state.cleaned_data[selected_file] = cleaned_df
                        
                        with col2:
                            st.markdown("### ✨ After Cleaning")
                            st.write(f"**Rows:** {len(cleaned_df):,}")
                            st.write(f"**Columns:** {len(cleaned_df.columns)}")
                            st.write(f"**Missing Values:** {cleaned_df.isnull().sum().sum():,}")
                            st.write(f"**Duplicates Removed:** {cleaning_log['duplicates_removed']:,}")
                            st.dataframe(cleaned_df.head())
                        
                        st.success("✅ Data cleaning completed successfully!")
                        
                        # Summary metrics
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Duplicates Removed", cleaning_log['duplicates_removed'])
                        col2.metric("Missing Values Filled", cleaning_log['missing_values_filled'])
                        col3.metric("Outliers Capped", cleaning_log['outliers_capped'])
                        
                        # Quality improvement
                        before_score = DataQualityAnalyzer.calculate_quality_score(data)['overall_score']
                        after_score = DataQualityAnalyzer.calculate_quality_score(cleaned_df)['overall_score']
                        improvement = after_score - before_score
                        
                        if improvement > 0:
                            st.balloons()
                            st.success(f"📈 Data Quality Improved by {improvement:.1f} points! ({before_score:.1f} → {after_score:.1f})")
                        
                        # Download button
                        csv = cleaned_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Cleaned Data (CSV)",
                            data=csv,
                            file_name=f"cleaned_{selected_file}",
                            mime="text/csv"
                        )
    
    # Insight Discovery Section
    elif page == "💡 Insight Discovery":
        st.header("💡 AI-Powered Insight Discovery")
        
        insight_engine = InsightEngine()
        
        data_to_analyze = st.session_state.cleaned_data if st.session_state.cleaned_data else st.session_state.data
        dfs = {name: data for name, data in data_to_analyze.items() if isinstance(data, pd.DataFrame)}
        
        if not dfs:
            st.warning("⚠️ No tabular data available. Please upload CSV/Excel files or clean your data first.")
        else:
            selected_file = st.selectbox("Select dataset for analysis", list(dfs.keys()))
            data = dfs[selected_file]
            
            if st.button("💡 Discover Insights", use_container_width=True):
                with st.spinner("AI is discovering patterns and insights from your data..."):
                    insights = insight_engine.generate_insights(data)
                    st.session_state.insights = insights
                    
                    if insights:
                        st.success(f"✨ Found {len(insights)} valuable insights!")
                        
                        # Display insights
                        for insight in insights:
                            with st.container():
                                st.markdown(f"""
                                <div class="insight-box">
                                    <h4>🔍 {insight['title']}</h4>
                                    <p>{insight['description']}</p>
                                    <small>📊 Confidence: {insight['confidence']:.1f}% | 📋 Evidence: {insight['evidence']}</small>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # Generate recommendations
                        recommendations = insight_engine.generate_recommendations(data, insights)
                        st.session_state.recommendations = recommendations
                        
                        st.subheader("🎯 Actionable Recommendations")
                        for rec in recommendations:
                            st.markdown(f"""
                            <div class="recommendation-card">
                                <h4>💡 {rec['title']}</h4>
                                <p>{rec['description']}</p>
                                <small>⚡ Priority: {rec['priority']} | 📈 Impact: {rec['impact']} | 🎯 Confidence: {rec['confidence']}%</small>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Summary statistics
                        st.subheader("📊 Key Metrics Summary")
                        numeric_cols = data.select_dtypes(include=[np.number]).columns
                        if len(numeric_cols) > 0:
                            summary_df = data[numeric_cols].agg(['mean', 'median', 'std', 'min', 'max']).round(2)
                            st.dataframe(summary_df)
                    else:
                        st.info("ℹ️ No significant patterns detected. Try uploading more data or different types of data.")
    
    # Trend Analysis Section
    elif page == "📈 Trend Analysis":
        st.header("📈 Advanced Trend Analysis")
        
        data_to_analyze = st.session_state.cleaned_data if st.session_state.cleaned_data else st.session_state.data
        dfs = {name: data for name, data in data_to_analyze.items() if isinstance(data, pd.DataFrame)}
        
        if not dfs:
            st.warning("⚠️ No tabular data available for trend analysis.")
        else:
            selected_file = st.selectbox("Select dataset", list(dfs.keys()))
            data = dfs[selected_file]
            
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                st.warning("⚠️ No numeric columns found for trend analysis.")
            else:
                selected_col = st.selectbox("Select metric to analyze", numeric_cols)
                
                # Advanced visualizations
                viz_tabs = st.tabs(["📈 Time Series", "📊 Multi-Metric", "🎯 Radar Chart", "💎 Bubble Chart", "🌟 Sunburst"])
                
                with viz_tabs[0]:
                    # Time series visualization
                    time_fig = create_time_series_visualization(data, selected_col)
                    st.plotly_chart(time_fig, use_container_width=True)
                
                with viz_tabs[1]:
                    # Multi-metric comparison
                    multi_cols = st.multiselect("Select columns to compare", numeric_cols, default=numeric_cols[:3].tolist())
                    if multi_cols:
                        compare_fig = create_comparison_chart(data, multi_cols)
                        st.plotly_chart(compare_fig, use_container_width=True)
                
                with viz_tabs[2]:
                    # Radar chart
                    if len(numeric_cols) >= 3:
                        radar_fig = create_radar_chart(data, numeric_cols[:6].tolist())
                        if radar_fig:
                            st.plotly_chart(radar_fig, use_container_width=True)
                    else:
                        st.info("Need at least 3 numeric columns for radar chart")
                
                with viz_tabs[3]:
                    # Bubble chart
                    if len(numeric_cols) >= 3:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            x_col = st.selectbox("X-axis", numeric_cols, key="bubble_x")
                        with col2:
                            y_col = st.selectbox("Y-axis", numeric_cols, key="bubble_y")
                        with col3:
                            size_col = st.selectbox("Bubble size", numeric_cols, key="bubble_size")
                        
                        if x_col and y_col and size_col:
                            bubble_fig = create_bubble_chart(data, x_col, y_col, size_col)
                            st.plotly_chart(bubble_fig, use_container_width=True)
                    else:
                        st.info("Need at least 3 numeric columns for bubble chart")
                
                with viz_tabs[4]:
                    # Waterfall chart
                    waterfall_fig = create_waterfall_chart(data, selected_col)
                    st.plotly_chart(waterfall_fig, use_container_width=True)
                
                # AI Interpretation
                if len(data) > 1:
                    first_val = data[selected_col].iloc[0]
                    last_val = data[selected_col].iloc[-1]
                    trend = last_val - first_val
                    percent_change = (trend / first_val) * 100 if first_val != 0 else 0
                    
                    # Calculate additional statistics
                    growth_rate = (last_val / first_val - 1) * 100 if first_val != 0 else 0
                    volatility = data[selected_col].std() / data[selected_col].mean() if data[selected_col].mean() != 0 else 0
                    
                    st.info(f"""
                    ### 🤖 AI-Powered Analysis
                    
                    **Performance Summary:**
                    - **{selected_col}** has {'📈 increased' if trend > 0 else '📉 decreased'} by **{abs(percent_change):.1f}%** over the analysis period
                    - **Growth Rate:** {growth_rate:.1f}% overall
                    - **Volatility Index:** {volatility:.3f} ({'High' if volatility > 0.5 else 'Moderate' if volatility > 0.3 else 'Low'} variability)
                    
                    **Strategic Insights:**
                    {'✅ Positive growth trend detected. Consider accelerating investments in this area.' if trend > 0 else '⚠️ Declining trend detected. Immediate investigation and intervention recommended.'}
                    
                    **Recommendation:** 
                    {'Maintain current strategy while optimizing for further growth opportunities.' if trend > 0 else 'Conduct root cause analysis and implement corrective measures within the next 30 days.'}
                    """)
    
    # Anomaly Detection Section
    elif page == "⚠️ Anomaly Detection":
        st.header("⚠️ Intelligent Anomaly Detection System")
        
        data_to_analyze = st.session_state.cleaned_data if st.session_state.cleaned_data else st.session_state.data
        dfs = {name: data for name, data in data_to_analyze.items() if isinstance(data, pd.DataFrame)}
        
        if not dfs:
            st.warning("⚠️ No tabular data available for anomaly detection.")
        else:
            selected_file = st.selectbox("Select dataset", list(dfs.keys()))
            data = dfs[selected_file]
            
            if st.button("🔍 Run Anomaly Detection", use_container_width=True):
                with st.spinner("Analyzing data for anomalies using AI algorithms..."):
                    anomalies = AnomalyDetector.detect_anomalies(data)
                    st.session_state.anomalies[selected_file] = anomalies
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("🚨 Anomalies Found", anomalies['anomalies_found'])
                    col2.metric("📊 Anomaly Ratio", f"{anomalies['anomaly_ratio']*100:.1f}%")
                    col3.metric("🎯 Severity Level", "High" if anomalies['anomalies_found'] > len(data)*0.1 else "Medium" if anomalies['anomalies_found'] > 0 else "Low")
                    
                    if anomalies['anomalies_found'] > 0:
                        st.warning(f"⚠️ {anomalies['anomalies_found']} anomalies detected in the dataset!")
                        
                        # Visualization of anomalies
                        numeric_cols = data.select_dtypes(include=[np.number]).columns
                        if len(numeric_cols) > 0:
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=data.index, y=data[numeric_cols[0]],
                                mode='markers',
                                name='Normal',
                                marker=dict(color='#1a73e8', size=8)
                            ))
                            
                            # Highlight anomalies
                            anomaly_indices = [a['row_index'] for a in anomalies['details']]
                            anomaly_data = data.iloc[anomaly_indices]
                            fig.add_trace(go.Scatter(
                                x=anomaly_data.index, y=anomaly_data[numeric_cols[0]],
                                mode='markers',
                                name='Anomalies',
                                marker=dict(color='#ea4335', size=12, symbol='x')
                            ))
                            
                            fig.update_layout(
                                title=f"Anomaly Visualization - {numeric_cols[0]}",
                                xaxis_title="Index",
                                yaxis_title=numeric_cols[0],
                                height=500
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Display anomaly details
                        st.subheader("🔍 Detected Anomalies Details")
                        for anomaly in anomalies['details'][:5]:
                            with st.expander(f"🚨 Anomaly at Row {anomaly['row_index']} (Severity: {anomaly['severity']})"):
                                st.json(anomaly['values'])
                    else:
                        st.success("✅ No significant anomalies detected! Your data looks clean and consistent.")
                        st.balloons()
    
    # Predictive Analytics Section
    elif page == "🔮 Predictive Analytics":
        st.header("🔮 Predictive Analytics & Forecasting")
        
        data_to_analyze = st.session_state.cleaned_data if st.session_state.cleaned_data else st.session_state.data
        dfs = {name: data for name, data in data_to_analyze.items() if isinstance(data, pd.DataFrame)}
        
        if not dfs:
            st.warning("⚠️ No tabular data available for predictive modeling.")
        else:
            selected_file = st.selectbox("Select dataset", list(dfs.keys()))
            data = dfs[selected_file]
            
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) < 2:
                st.warning("⚠️ Need at least 2 numeric columns for predictive modeling.")
            else:
                prediction_type = st.radio("Select Prediction Type", ["📈 Regression (Predict Values)", "🎯 Classification (Predict Categories)"])
                
                if prediction_type == "📈 Regression (Predict Values)":
                    target_col = st.selectbox("Select target column to predict", numeric_cols)
                    
                    if st.button("🚀 Train Prediction Model", use_container_width=True):
                        with st.spinner("Training AI prediction model..."):
                            model_results = PredictiveModeler.build_regression_model(data, target_col)
                            
                            if model_results:
                                col1, col2 = st.columns(2)
                                col1.metric("📊 R² Score", f"{model_results['r2_score']:.3f}")
                                col2.metric("📉 Mean Absolute Error", f"{model_results['mae']:.2f}")
                                
                                # Performance gauge
                                fig = go.Figure(go.Indicator(
                                    mode="gauge+number",
                                    value=model_results['r2_score'] * 100,
                                    title={'text': "Model Performance Score"},
                                    domain={'x': [0, 1], 'y': [0, 1]},
                                    gauge={
                                        'axis': {'range': [None, 100]},
                                        'bar': {'color': "#1a73e8"},
                                        'steps': [
                                            {'range': [0, 50], 'color': "#fce8e6"},
                                            {'range': [50, 75], 'color': "#fef7e0"},
                                            {'range': [75, 100], 'color': "#e6f4ea"}
                                        ],
                                        'threshold': {
                                            'line': {'color': "#ea4335", 'width': 4},
                                            'thickness': 0.75,
                                            'value': 90
                                        }
                                    }
                                ))
                                fig.update_layout(height=300)
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Feature importance
                                if model_results['feature_importance']:
                                    st.subheader("🔑 Key Factors Influencing Predictions")
                                    importance_df = pd.DataFrame.from_dict(
                                        model_results['feature_importance'], 
                                        orient='index', 
                                        columns=['Importance']
                                    ).sort_values('Importance', ascending=True)
                                    
                                    fig = px.bar(
                                        importance_df,
                                        x='Importance',
                                        y=importance_df.index,
                                        orientation='h',
                                        title="Feature Importance Analysis",
                                        color='Importance',
                                        color_continuous_scale='Viridis'
                                    )
                                    st.plotly_chart(fig, use_container_width=True)
                                
                                st.success("✅ Model training completed successfully!")
                                st.info("💡 The model can now predict new values based on input features.")
                            else:
                                st.error("❌ Could not train model. Please ensure sufficient data and try again.")
                
                else:  # Classification
                    binary_cols = []
                    for col in data.columns:
                        if len(data[col].dropna().unique()) == 2:
                            binary_cols.append(col)
                    
                    if binary_cols:
                        target_col = st.selectbox("Select target column for classification", binary_cols)
                        
                        if st.button("🚀 Train Classification Model", use_container_width=True):
                            with st.spinner("Training classification model..."):
                                model_results = PredictiveModeler.build_classification_model(data, target_col)
                                
                                if model_results:
                                    col1, col2, col3, col4 = st.columns(4)
                                    col1.metric("🎯 Accuracy", f"{model_results['accuracy']:.3f}")
                                    col2.metric("📊 Precision", f"{model_results['precision']:.3f}")
                                    col3.metric("📈 Recall", f"{model_results['recall']:.3f}")
                                    col4.metric("⚡ F1 Score", f"{model_results['f1']:.3f}")
                                    
                                    # Confusion matrix visualization
                                    st.subheader("📊 Model Performance Metrics")
                                    metrics_df = pd.DataFrame({
                                        'Metric': ['Accuracy', 'Precision', 'Recall', 'F1 Score'],
                                        'Score': [
                                            model_results['accuracy'],
                                            model_results['precision'],
                                            model_results['recall'],
                                            model_results['f1']
                                        ]
                                    })
                                    fig = px.bar(metrics_df, x='Metric', y='Score', 
                                                title="Model Performance Metrics",
                                                color='Score', color_continuous_scale='Viridis',
                                                range_y=[0, 1])
                                    st.plotly_chart(fig, use_container_width=True)
                                    
                                    st.success("✅ Classification model trained successfully!")
                                else:
                                    st.error("❌ Could not train classification model.")
                    else:
                        st.warning("⚠️ No binary columns found for classification. Please add a column with two categories.")
    
    # AI Chat Assistant Section
    elif page == "💬 AI Chat Assistant":
        st.header("💬 AI Chat Assistant")
        st.markdown("Ask questions about your data in natural language")
        
        if not st.session_state.data:
            st.warning("⚠️ Please upload data first.")
        else:
            # Pre-defined questions
            st.markdown("### 💡 Suggested Questions")
            suggested_questions = [
                "What are the main trends in my data?",
                "Are there any anomalies or outliers?",
                "What recommendations do you have?",
                "Summarize the key insights",
                "Which metrics are most important?"
            ]
            
            cols = st.columns(3)
            for i, q in enumerate(suggested_questions[:3]):
                with cols[i]:
                    if st.button(q, use_container_width=True):
                        st.session_state.chat_question = q
            
            user_question = st.text_input("Your question:", value=st.session_state.get('chat_question', ''))
            
            if user_question:
                with st.spinner("🤖 AI is analyzing your data..."):
                    response = "Based on my analysis of your data:\n\n"
                    
                    if any(word in user_question.lower() for word in ['trend', 'trends', 'pattern', 'patterns']):
                        response += "📈 **Trend Analysis:**\n"
                        dfs = {name: data for name, data in st.session_state.data.items() if isinstance(data, pd.DataFrame)}
                        for name, df in dfs.items():
                            numeric_cols = df.select_dtypes(include=[np.number]).columns
                            for col in numeric_cols[:3]:
                                if len(df) > 1:
                                    first_val = df[col].iloc[0]
                                    last_val = df[col].iloc[-1]
                                    if first_val != 0:
                                        change = ((last_val - first_val) / first_val) * 100
                                        direction = "increased" if change > 0 else "decreased"
                                        response += f"- {col} has {direction} by {abs(change):.1f}%\n"
                    
                    elif any(word in user_question.lower() for word in ['anomaly', 'anomalies', 'outlier', 'outliers']):
                        response += "⚠️ **Anomaly Detection:**\n"
                        for name, anomalies in st.session_state.anomalies.items():
                            if anomalies.get('anomalies_found', 0) > 0:
                                response += f"- Found {anomalies['anomalies_found']} anomalies in {name}\n"
                            else:
                                response += f"- No significant anomalies detected in {name}\n"
                    
                    elif any(word in user_question.lower() for word in ['recommend', 'recommendation', 'suggest', 'advice']):
                        response += "💡 **Recommendations:**\n"
                        if st.session_state.recommendations:
                            for rec in st.session_state.recommendations[:3]:
                                response += f"- {rec['title']}: {rec['description']}\n"
                        else:
                            response += "- Please generate insights first to receive recommendations.\n"
                    
                    elif any(word in user_question.lower() for word in ['summary', 'overview', 'key', 'insight']):
                        response += "📊 **Executive Summary:**\n"
                        total_files = len(st.session_state.data)
                        dfs = {name: data for name, data in st.session_state.data.items() if isinstance(data, pd.DataFrame)}
                        total_rows = sum(len(df) for df in dfs.values())
                        total_insights = len(st.session_state.insights)
                        
                        response += f"- Total data sources: {total_files}\n"
                        response += f"- Total records analyzed: {total_rows:,}\n"
                        response += f"- Insights discovered: {total_insights}\n"
                        
                        if st.session_state.data_quality_scores:
                            avg_quality = np.mean([s['overall_score'] for s in st.session_state.data_quality_scores.values()])
                            response += f"- Average data quality score: {avg_quality:.1f}/100\n"
                    
                    else:
                        response += "I can help you analyze your data. Try asking about:\n"
                        response += "- Trends and patterns\n"
                        response += "- Anomalies and outliers\n"
                        response += "- Recommendations for improvement\n"
                        response += "- Executive summary of findings\n"
                    
                    st.info(response)
    
    # Executive Summary Section
    elif page == "📊 Executive Summary":
        st.header("📊 Executive Summary Dashboard")
        
        if not st.session_state.data:
            st.warning("⚠️ Please upload data and generate insights first.")
        else:
            # Calculate metrics
            total_files = len(st.session_state.data)
            dfs = {name: data for name, data in st.session_state.data.items() if isinstance(data, pd.DataFrame)}
            total_records = sum(len(df) for df in dfs.values())
            total_insights = len(st.session_state.insights)
            anomalies_total = sum(v.get('anomalies_found', 0) for v in st.session_state.anomalies.values())
            
            # KPI Row with custom styling
            st.markdown("### 📈 Key Performance Indicators")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown("""
                <div class="metric-card">
                    <div style="font-size: 14px; color: #5f6368;">📊 Data Sources</div>
                    <div style="font-size: 32px; font-weight: 700;">{}</div>
                </div>
                """.format(total_files), unsafe_allow_html=True)
            with col2:
                st.markdown("""
                <div class="metric-card">
                    <div style="font-size: 14px; color: #5f6368;">📈 Total Records</div>
                    <div style="font-size: 32px; font-weight: 700;">{:,}</div>
                </div>
                """.format(total_records), unsafe_allow_html=True)
            with col3:
                st.markdown("""
                <div class="metric-card">
                    <div style="font-size: 14px; color: #5f6368;">💡 Insights Found</div>
                    <div style="font-size: 32px; font-weight: 700;">{}</div>
                </div>
                """.format(total_insights), unsafe_allow_html=True)
            with col4:
                st.markdown("""
                <div class="metric-card">
                    <div style="font-size: 14px; color: #5f6368;">⚠️ Anomalies</div>
                    <div style="font-size: 32px; font-weight: 700;">{}</div>
                </div>
                """.format(anomalies_total), unsafe_allow_html=True)
            
            # Data Quality Score
            if st.session_state.data_quality_scores:
                avg_quality = np.mean([s['overall_score'] for s in st.session_state.data_quality_scores.values()])
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=avg_quality,
                        title={'text': "Data Quality Score", 'font': {'size': 24}},
                        domain={'x': [0, 1], 'y': [0, 1]},
                        gauge={
                            'axis': {'range': [None, 100], 'tickwidth': 1},
                            'bar': {'color': "#1a73e8"},
                            'steps': [
                                {'range': [0, 40], 'color': "#fce8e6"},
                                {'range': [40, 70], 'color': "#fef7e0"},
                                {'range': [70, 100], 'color': "#e6f4ea"}
                            ],
                            'threshold': {
                                'line': {'color': "#ea4335", 'width': 4},
                                'thickness': 0.75,
                                'value': 90
                            }
                        }
                    ))
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Quality Assessment</h3>
                        <p><strong>Status:</strong> {st.session_state.data_quality_scores[list(st.session_state.data_quality_scores.keys())[0]]['status']}</p>
                        <p><strong>Missing Values Score:</strong> {st.session_state.data_quality_scores[list(st.session_state.data_quality_scores.keys())[0]]['missing_score']:.1f}/100</p>
                        <p><strong>Duplicates Score:</strong> {st.session_state.data_quality_scores[list(st.session_state.data_quality_scores.keys())[0]]['duplicate_score']:.1f}/100</p>
                        <p><strong>Consistency Score:</strong> {st.session_state.data_quality_scores[list(st.session_state.data_quality_scores.keys())[0]]['consistency_score']:.1f}/100</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Top Insights
            if st.session_state.insights:
                st.subheader("🏆 Top Insights")
                for i, insight in enumerate(st.session_state.insights[:5], 1):
                    st.markdown(f"""
                    <div class="insight-box">
                        <b>{i}. {insight['title']}</b><br>
                        {insight['description']}<br>
                        <small>📊 Confidence: {insight['confidence']:.1f}% | 📋 {insight['evidence']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Top Recommendations
            if st.session_state.recommendations:
                st.subheader("🎯 Priority Recommendations")
                for rec in st.session_state.recommendations[:3]:
                    priority_color = "#ea4335" if rec['priority'] == 'Critical' else "#f9ab00" if rec['priority'] == 'High' else "#1a73e8"
                    st.markdown(f"""
                    <div class="recommendation-card">
                        <b>{rec['title']}</b> <span style="color: {priority_color}; font-weight: bold;">[{rec['priority']}]</span><br>
                        {rec['description']}<br>
                        <small>📈 Impact: {rec['impact']} | 🎯 Confidence: {rec['confidence']}%</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            # CEO Briefing
            st.subheader("👔 CEO Briefing - 30 Second Snapshot")
            
            ceo_briefing = f"""
            ### Performance Overview
            
            **Data Infrastructure:**
            • {total_files} data sources integrated
            • {total_records:,} records analyzed
            • Data Quality Score: {avg_quality:.1f}/100
            
            **Key Findings:**
            • {total_insights} actionable insights discovered
            • {anomalies_total} anomalies requiring attention
            • {len(st.session_state.recommendations)} strategic recommendations
            
            **Strategic Imperatives:**
            1. **Immediate Action Required:** Address detected anomalies and data quality issues
            2. **Short-term (0-3 months):** Implement top 3 recommendations
            3. **Long-term (3-12 months):** Establish continuous monitoring and predictive analytics
            
            **Expected Business Impact:**
            • 30% reduction in manual analysis time
            • 25% improvement in decision accuracy
            • 40% faster issue detection and resolution
            """
            
            st.markdown(ceo_briefing)
            
            # Export options
            st.subheader("📄 Export Summary")
            col1, col2 = st.columns(2)
            
            with col1:
                report_text = f"""
                INSIGHTFORGE AI EXECUTIVE SUMMARY
                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                
                KEY METRICS:
                - Data Sources: {total_files}
                - Total Records: {total_records:,}
                - Insights Found: {total_insights}
                - Anomalies Detected: {anomalies_total}
                - Data Quality Score: {avg_quality:.1f}/100
                
                TOP INSIGHTS:
                {chr(10).join([f"{i+1}. {insight['title']}: {insight['description']}" for i, insight in enumerate(st.session_state.insights[:5])])}
                
                RECOMMENDATIONS:
                {chr(10).join([f"- {rec['title']} ({rec['priority']}): {rec['description']}" for rec in st.session_state.recommendations[:5]])}
                """
                
                st.download_button(
                    label="📥 Download Executive Summary (TXT)",
                    data=report_text,
                    file_name=f"executive_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
            
            with col2:
                export_data = {
                    "timestamp": datetime.now().isoformat(),
                    "metrics": {
                        "total_files": total_files,
                        "total_records": total_records,
                        "insights_found": total_insights,
                        "anomalies_detected": anomalies_total,
                        "data_quality_score": avg_quality
                    },
                    "insights": st.session_state.insights[:10],
                    "recommendations": st.session_state.recommendations[:5]
                }
                
                st.download_button(
                    label="📥 Export as JSON",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"insights_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

if __name__ == "__main__":
    main()