"""
Model Training Module for INESData Dataspace
Interactive machine learning model training and prediction on downloaded datasets
"""
import io
import pickle
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.svm import SVC, SVR
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, r2_score, confusion_matrix, classification_report
)
from sklearn.decomposition import PCA


class ModelTrainer:
    """Interactive ML model training and prediction"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.encoders = {}
        self.feature_names = None
        self.target_name = None
        self.model_type = None
        self.metrics = {}
    
    def load_data(self, csv_data: bytes) -> pd.DataFrame:
        """Load CSV data from bytes"""
        try:
            df = pd.read_csv(io.BytesIO(csv_data))
            return df
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return None
    
    def get_data_summary(self, df: pd.DataFrame) -> dict:
        """Get comprehensive data summary"""
        return {
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'numeric_cols': df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_cols': df.select_dtypes(include=['object']).columns.tolist(),
            'numeric_stats': df.describe().to_dict()
        }
    
    def prepare_data(self, df: pd.DataFrame, target_col: str, problem_type: str = 'classification',
                    test_size: float = 0.2, random_state: int = 42):
        """Prepare data for training with proper shuffling and stratification"""
        try:
            # Handle missing values
            df = df.dropna()
            
            if len(df) == 0:
                st.error("No rows left after removing missing values")
                return None, None, None, None, None
            
            # Separate features and target
            X = df.drop(columns=[target_col])
            y = df[target_col]
            
            self.target_name = target_col
            
            # Encode categorical features
            for col in X.select_dtypes(include=['object']).columns:
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))
                self.encoders[col] = le
            
            # Encode target if categorical
            if y.dtype == 'object':
                le = LabelEncoder()
                y = le.fit_transform(y.astype(str))
                self.encoders['target'] = le
            
            self.feature_names = X.columns.tolist()
            
            # Split data with proper shuffling and stratification
            # stratify for classification ensures balanced class distribution
            stratify_col = y if problem_type == 'classification' else None
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, 
                test_size=test_size, 
                random_state=random_state,
                shuffle=True,  # Explicit shuffle for reproducibility
                stratify=stratify_col  # Balance classes in classification
            )
            
            # Scale features
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            return X_train_scaled, X_test_scaled, y_train, y_test, X
            
        except Exception as e:
            st.error(f"Error preparing data: {str(e)}")
            return None, None, None, None, None
    
    def train_model(self, X_train, X_test, y_train, y_test, 
                   model_name: str, problem_type: str, **kwargs):
        """Train ML model"""
        try:
            self.model_type = model_name
            
            # Classification models
            if problem_type == 'classification':
                if model_name == 'Random Forest':
                    self.model = RandomForestClassifier(
                        n_estimators=kwargs.get('n_estimators', 100),
                        max_depth=kwargs.get('max_depth', 10),
                        random_state=42,
                        n_jobs=-1
                    )
                elif model_name == 'SVM':
                    self.model = SVC(
                        kernel=kwargs.get('kernel', 'rbf'),
                        C=kwargs.get('C', 1.0),
                        random_state=42
                    )
                elif model_name == 'Logistic Regression':
                    self.model = LogisticRegression(
                        max_iter=kwargs.get('max_iter', 1000),
                        random_state=42,
                        n_jobs=-1
                    )
            
            # Regression models
            elif problem_type == 'regression':
                if model_name == 'Random Forest':
                    self.model = RandomForestRegressor(
                        n_estimators=kwargs.get('n_estimators', 100),
                        max_depth=kwargs.get('max_depth', 10),
                        random_state=42,
                        n_jobs=-1
                    )
                elif model_name == 'SVM':
                    self.model = SVR(
                        kernel=kwargs.get('kernel', 'rbf'),
                        C=kwargs.get('C', 1.0)
                    )
                elif model_name == 'Linear Regression':
                    self.model = LinearRegression(n_jobs=-1)
            
            # Train model
            self.model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.model.predict(X_test)
            
            if problem_type == 'classification':
                self.metrics = {
                    'accuracy': accuracy_score(y_test, y_pred),
                    'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
                    'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
                    'f1': f1_score(y_test, y_pred, average='weighted', zero_division=0)
                }
            else:  # regression
                self.metrics = {
                    'mse': mean_squared_error(y_test, y_pred),
                    'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                    'r2': r2_score(y_test, y_pred),
                    'mae': np.mean(np.abs(y_test - y_pred))
                }
            
            return True, y_pred, y_test
            
        except Exception as e:
            st.error(f"Error training model: {str(e)}")
            return False, None, None
    
    def predict(self, input_data: dict) -> tuple:
        """Make prediction on new data"""
        try:
            if self.model is None:
                return False, "Model not trained yet"
            
            # Create feature vector
            feature_vector = []
            for feature in self.feature_names:
                if feature in input_data:
                    value = input_data[feature]
                    # Encode if needed
                    if feature in self.encoders:
                        value = self.encoders[feature].transform([value])[0]
                    feature_vector.append(value)
                else:
                    feature_vector.append(0)
            
            # Scale
            feature_vector = np.array(feature_vector).reshape(1, -1)
            feature_vector = self.scaler.transform(feature_vector)
            
            # Predict
            prediction = self.model.predict(feature_vector)[0]
            
            # Decode if target was encoded
            if 'target' in self.encoders:
                prediction = self.encoders['target'].inverse_transform([prediction])[0]
            
            # Get prediction confidence if classification
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(feature_vector)[0]
                confidence = np.max(probabilities)
                return True, prediction, confidence
            else:
                return True, prediction, None
            
        except Exception as e:
            return False, str(e), None
    
    def get_feature_importance(self):
        """Get feature importance if available"""
        try:
            if hasattr(self.model, 'feature_importances_'):
                importances = self.model.feature_importances_
                feature_importance_df = pd.DataFrame({
                    'feature': self.feature_names,
                    'importance': importances
                }).sort_values('importance', ascending=False)
                return feature_importance_df
            return None
        except:
            return None
    
    def visualize_feature_importance(self, top_n: int = 10):
        """Visualize feature importance"""
        fi_df = self.get_feature_importance()
        if fi_df is not None and len(fi_df) > 0:
            fig, ax = plt.subplots(figsize=(10, 6))
            fi_df.head(top_n).plot(x='feature', y='importance', kind='barh', ax=ax, legend=False)
            ax.set_xlabel('Importance')
            ax.set_ylabel('Feature')
            ax.set_title(f'Top {top_n} Feature Importance')
            return fig
        return None
    
    def visualize_confusion_matrix(self, y_test, y_pred):
        """Visualize confusion matrix for classification"""
        try:
            cm = confusion_matrix(y_test, y_pred)
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax, cbar_kws={'label': 'Count'})
            ax.set_xlabel('Predicted')
            ax.set_ylabel('Actual')
            ax.set_title('Confusion Matrix')
            return fig
        except:
            return None
    
    def visualize_predictions(self, y_test, y_pred):
        """Visualize actual vs predicted values"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(y_test, y_pred, alpha=0.6)
        # Add diagonal line
        min_val = min(y_test.min(), y_pred.min())
        max_val = max(y_test.max(), y_pred.max())
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect Prediction')
        ax.set_xlabel('Actual Values')
        ax.set_ylabel('Predicted Values')
        ax.set_title('Actual vs Predicted Values')
        ax.legend()
        ax.grid(True, alpha=0.3)
        return fig
    
    def save_model(self) -> bytes:
        """Serialize model to bytes"""
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'encoders': self.encoders,
                'feature_names': self.feature_names,
                'target_name': self.target_name,
                'model_type': self.model_type,
                'metrics': self.metrics
            }
            return pickle.dumps(model_data)
        except Exception as e:
            st.error(f"Error saving model: {str(e)}")
            return None
    
    def load_model(self, model_bytes: bytes) -> bool:
        """Load model from bytes"""
        try:
            model_data = pickle.loads(model_bytes)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.encoders = model_data['encoders']
            self.feature_names = model_data['feature_names']
            self.target_name = model_data['target_name']
            self.model_type = model_data['model_type']
            self.metrics = model_data['metrics']
            return True
        except Exception as e:
            st.error(f"Error loading model: {str(e)}")
            return False
