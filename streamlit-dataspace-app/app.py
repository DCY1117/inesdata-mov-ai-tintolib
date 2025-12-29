"""
INESData Dataspace Browser with TINTOlib Integration
Enterprise-grade dataspace catalog browser with automated contract negotiation,
data transfer, and synthetic image generation for machine learning.
"""
import streamlit as st
import pandas as pd
import pickle
from auth import KeycloakAuth
from edc_client import EDCClient
from tinto_processor import TINTOProcessor
from model_trainer import ModelTrainer
from config import KEYCLOAK_REALM

# Page configuration
st.set_page_config(
    page_title="INESData Dataspace Browser | TINTOlib ML Integration",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #1f77b4;
        --secondary-color: #ff7f0e;
        --success-color: #2ca02c;
        --warning-color: #d62728;
    }
    
    /* Headers */
    h1 {
        color: #1f77b4;
        font-weight: 600;
        padding-bottom: 0.5rem;
    }
    
    h2 {
        color: #2c3e50;
        font-weight: 500;
        margin-top: 1.5rem;
    }
    
    /* Cards and containers */
    .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Download buttons */
    .stDownloadButton > button {
        background-color: #2ca02c;
        color: white;
        border-radius: 6px;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 600;
    }
    
    /* Progress bars */
    .stProgress > div > div {
        background-color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'catalog' not in st.session_state:
    st.session_state.catalog = None

# Initialize auth client
auth_client = KeycloakAuth()


def login_page():
    """Display modern login page with branding"""
    # Hero section
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='font-size: 2.5rem; margin-bottom: 0;'>🔬 INESData Dataspace</h1>
            <p style='font-size: 1.2rem; color: #666; margin-top: 0.5rem;'>
                Enterprise Data Marketplace with ML Integration
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Features overview
        feat_col1, feat_col2, feat_col3 = st.columns(3)
        with feat_col1:
            st.markdown("**📚 Browse**")
            st.caption("Explore datasets")
        with feat_col2:
            st.markdown("**🤝 Negotiate**")
            st.caption("Automated contracts")
        with feat_col3:
            st.markdown("**🎨 Process**")
            st.caption("TINTOlib ML ready")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Login form
        with st.container():
            st.markdown("### 🔐 Consumer Authentication")
            
            with st.form("login_form"):
                username = st.text_input(
                    "👤 Username",
                    placeholder="user-conn-oeg-consumer",
                    help="Your Keycloak username for the consumer connector"
                )
                password = st.text_input(
                    "🔑 Password",
                    type="password",
                    placeholder="Enter your password",
                    help="Your Keycloak password"
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("🚀 Sign In", use_container_width=True, type="primary")
                
                if submitted:
                    if not username or not password:
                        st.error("⚠️ Please enter both username and password")
                    else:
                        with st.spinner("🔄 Authenticating with Keycloak..."):
                            token_data = auth_client.get_token(username, password)
                            
                            if token_data and 'access_token' in token_data:
                                st.session_state.authenticated = True
                                st.session_state.access_token = token_data['access_token']
                                st.session_state.refresh_token = token_data.get('refresh_token')
                                st.session_state.username = username
                                st.success("✅ Authentication successful! Redirecting...")
                                st.rerun()
                            else:
                                st.error("❌ Authentication failed. Please verify your credentials.")
            
            # System info
            with st.expander("ℹ️ System Information"):
                st.markdown(f"""
                - **Realm:** `{KEYCLOAK_REALM}`
                - **Default User:** `user-conn-oeg-consumer`
                - **Default Password:** `vCV!otahBte*!c@9`
                - **Connector:** Consumer (Port 30180)
                """)


def catalog_page():
    """Display modern catalog browsing page with metrics"""
    # Professional header with user info and logout
    header_col1, header_col2, header_col3 = st.columns([3, 2, 1])
    
    with header_col1:
        st.title("🔬 INESData Dataspace")
        st.caption("Enterprise Data Marketplace & ML Integration Platform")
    
    with header_col2:
        st.markdown(f"""
        <div style='text-align: right; padding-top: 1rem;'>
            <p style='margin: 0; color: #666;'>Signed in as</p>
            <p style='margin: 0; font-weight: 600; color: #1f77b4;'>👤 {st.session_state.username}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with header_col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Sign Out", use_container_width=True):
            for key in ['authenticated', 'access_token', 'username', 'catalog', 'negotiations', 'transfers']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    st.markdown("---")
    
    # Initialize EDC client
    auth_headers = auth_client.get_auth_headers(st.session_state.access_token)
    edc_client = EDCClient(auth_headers)
    
    # Downloaded Datasets section with metrics
    st.header("💾 My Downloaded Datasets")
    
    # Always show refresh button
    col_header1, col_header2 = st.columns([5, 1])
    with col_header2:
        if st.button("🔄 Refresh", key="refresh_downloads", use_container_width=True):
            st.rerun()
    
    # Check if there are any downloaded datasets
    downloaded_datasets = []
    if 'transfers' in st.session_state:
        for dataset_id, transfer_info in st.session_state.transfers.items():
            if transfer_info.get('downloaded_data'):
                # Find dataset info from catalog
                dataset_info = next((d for d in st.session_state.catalog if d['id'] == dataset_id), None) if st.session_state.catalog else None
                downloaded_datasets.append({
                    'id': dataset_id,
                    'name': dataset_info['name'] if dataset_info else dataset_id,
                    'filename': dataset_info.get('filename') if dataset_info else 'Unknown',
                    'format': dataset_info.get('format', 'data') if dataset_info else 'data',
                    'size': len(transfer_info['downloaded_data']),
                    'has_tinto': 'tinto_images' in transfer_info,
                    'transfer_info': transfer_info,
                    'dataset_info': dataset_info
                })
    
    if downloaded_datasets:
        # Metrics dashboard
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.metric("📊 Total Datasets", len(downloaded_datasets))
        with metric_col2:
            processed_count = sum(1 for d in downloaded_datasets if d['has_tinto'])
            st.metric("✨ Processed", processed_count)
        with metric_col3:
            total_size = sum(d['size'] for d in downloaded_datasets)
            st.metric("💿 Total Size", f"{total_size / 1024:.1f} KB")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Display as cards
        cols = st.columns(min(3, len(downloaded_datasets)))
        for idx, ds in enumerate(downloaded_datasets):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"**{ds['name']}**")
                    st.caption(f"ID: `{ds['id']}`")
                    if ds['filename'] != 'Unknown':
                        st.caption(f"📄 {ds['filename']}")
                    st.caption(f"Size: {ds['size']:,} bytes")
                    
                    # Action buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        # Download button
                        st.download_button(
                            label="💾 Save",
                            data=ds['transfer_info']['downloaded_data'],
                            file_name=f"{ds['filename']}" if ds['filename'] != 'Unknown' else f"{ds['name']}.{ds['format']}",
                            mime="application/octet-stream",
                            use_container_width=True,
                            key=f"save_quick_{ds['id']}"
                        )
                    with col2:
                        # Process button with popover
                        with st.popover("🎨 Process", use_container_width=True):
                            st.markdown("**TINTOlib Configuration**")
                            
                            method = st.selectbox(
                                "Method", 
                                ["TINTO", "IGTD", "REFINED", "BarGraph", "DistanceMatrix", 
                                 "Combination", "SuperTML", "FeatureWrap", "BIE"],
                                key=f"quick_method_{ds['id']}"
                            )
                            
                            problem = st.selectbox("Problem", ["supervised", "unsupervised", "regression"], key=f"quick_problem_{ds['id']}")
                            normalize = st.checkbox("Normalize", value=True, key=f"quick_normalize_{ds['id']}")
                            
                            # Method-specific parameters
                            method_params = {}
                            
                            if method == "TINTO":
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    method_params['algorithm'] = st.selectbox("Algorithm", ["PCA", "t-SNE"], key=f"quick_algo_{ds['id']}")
                                    method_params['pixels'] = st.slider("Pixels", 5, 100, 20, key=f"quick_pixels_{ds['id']}")
                                    method_params['blur'] = st.checkbox("Apply Blur", value=False, key=f"quick_blur_{ds['id']}")
                                    if method_params['blur']:
                                        method_params['steps'] = st.slider("Blur Steps", 1, 10, 4, key=f"quick_steps_{ds['id']}")
                                        method_params['option'] = st.selectbox("Blur Option", ["mean", "maximum"], key=f"quick_option_{ds['id']}")
                                with col_b:
                                    method_params['submatrix'] = st.checkbox("Submatrix", value=True, key=f"quick_submatrix_{ds['id']}")
                                    if method_params['blur']:
                                        method_params['amplification'] = st.number_input("Amplification", value=3.14159, format="%.5f", key=f"quick_amp_{ds['id']}")
                                        method_params['distance'] = st.slider("Distance", 1, 10, 2, key=f"quick_dist_{ds['id']}")
                                    if method_params.get('algorithm') == 't-SNE':
                                        method_params['times'] = st.slider("Times (t-SNE)", 1, 10, 4, key=f"quick_times_{ds['id']}")
                            
                            elif method == "IGTD":
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    scale_row = st.slider("Scale (rows)", 3, 20, 6, key=f"quick_scale_row_{ds['id']}")
                                    scale_col = st.slider("Scale (cols)", 3, 20, 6, key=f"quick_scale_col_{ds['id']}")
                                    method_params['scale'] = [scale_row, scale_col]
                                    method_params['fea_dist_method'] = st.selectbox("Feature Distance", ["Pearson", "Spearman", "Euclidean", "set"], key=f"quick_fea_{ds['id']}")
                                    method_params['image_dist_method'] = st.selectbox("Image Distance", ["Euclidean", "Manhattan"], key=f"quick_img_{ds['id']}")
                                with col_b:
                                    method_params['error'] = st.selectbox("Error Function", ["squared", "abs"], key=f"quick_error_{ds['id']}")
                                    method_params['max_step'] = st.slider("Max Steps", 100, 5000, 1000, key=f"quick_maxstep_{ds['id']}")
                                    method_params['val_step'] = st.slider("Val Steps", 10, 200, 50, key=f"quick_valstep_{ds['id']}")
                                    method_params['min_gain'] = st.number_input("Min Gain", value=0.00001, format="%.5f", key=f"quick_mingain_{ds['id']}")
                            
                            elif method == "REFINED":
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    method_params['hcIterations'] = st.slider("HC Iterations", 1, 100, 5, key=f"quick_hc_{ds['id']}")
                                with col_b:
                                    method_params['n_processors'] = st.slider("Processors", 2, 16, 8, key=f"quick_proc_{ds['id']}")
                            
                            elif method == "BarGraph":
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    method_params['pixel_width'] = st.slider("Pixel Width", 1, 20, 1, key=f"quick_pw_{ds['id']}")
                                with col_b:
                                    method_params['gap'] = st.slider("Gap", 0, 20, 0, key=f"quick_gap_{ds['id']}")
                            
                            elif method == "DistanceMatrix":
                                st.info("DistanceMatrix uses default parameters with normalize and zoom.")
                            
                            elif method == "Combination":
                                st.info("Combination uses default parameters with normalize and zoom.")
                            
                            elif method == "SuperTML":
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    method_params['pixels'] = st.slider("Pixels", 50, 500, 224, key=f"quick_pixels_stml_{ds['id']}")
                                    method_params['font_size'] = st.slider("Font Size", 5, 30, 10, key=f"quick_font_{ds['id']}")
                                with col_b:
                                    method_params['feature_importance'] = st.checkbox("Feature Importance (Variable Font)", value=False, key=f"quick_feat_imp_{ds['id']}")
                                    st.caption("False: SuperTML-EF (Equal Font)")
                                    st.caption("True: SuperTML-VF (Variable Font)")
                            
                            elif method == "FeatureWrap":
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    size_row = st.slider("Size (rows)", 2, 50, 8, key=f"quick_size_row_{ds['id']}")
                                    size_col = st.slider("Size (cols)", 2, 50, 8, key=f"quick_size_col_{ds['id']}")
                                    method_params['size'] = (size_row, size_col)
                                with col_b:
                                    method_params['bins'] = st.slider("Bins", 2, 100, 10, key=f"quick_bins_{ds['id']}")
                                    st.caption(f"Image size: {size_row}x{size_col} pixels")
                            
                            elif method == "BIE":
                                method_params['precision'] = st.selectbox("Precision", [32, 64], index=0, key=f"quick_prec_{ds['id']}")
                                st.caption("Binary encoding precision for data representation")
                            
                            # Common zoom parameter for all methods
                            method_params['zoom'] = st.slider("Zoom", 1, 10, 1, key=f"quick_zoom_{ds['id']}")
                            
                            if st.button("🚀 Generate Images", key=f"quick_gen_{ds['id']}", use_container_width=True):
                                with st.spinner("Processing with TINTOlib..."):
                                    processor = TINTOProcessor()
                                    
                                    images = processor.process_data(
                                        csv_data=ds['transfer_info']['downloaded_data'],
                                        method=method,
                                        problem=problem,
                                        normalize=normalize,
                                        **method_params
                                    )
                                    
                                    if images:
                                        st.session_state.transfers[ds['id']]['tinto_images'] = images
                                        st.success("✨ Images generated!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to generate images")
                    
                    # Show status badges
                    if ds['has_tinto']:
                        st.success("✨ Processed", icon="✅")
                        num_images = len(ds['transfer_info'].get('tinto_images', []))
                        st.caption(f"📸 {num_images} images generated")
                    else:
                        st.info("⏳ Ready to process", icon="ℹ️")
    else:
        st.info("📭 No datasets downloaded yet. Browse the catalog below to download data.")
    
    # Display generated images section
    if downloaded_datasets:
        processed_datasets = [ds for ds in downloaded_datasets if ds['has_tinto']]
        if processed_datasets:
            st.markdown("### 🖼️ Generated Synthetic Images")
            
            for ds in processed_datasets:
                with st.expander(f"📸 {ds['name']} - Images", expanded=True):
                    processor = TINTOProcessor()
                    processor.display_images(ds['transfer_info']['tinto_images'], max_display=12)
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.caption(f"Total images: {len(ds['transfer_info']['tinto_images'])}")
                    with col2:
                        if st.button("🗑️ Clear", key=f"clear_images_{ds['id']}", use_container_width=True):
                            processor.cleanup()
                            if 'tinto_images' in st.session_state.transfers[ds['id']]:
                                del st.session_state.transfers[ds['id']]['tinto_images']
                            st.success("Images cleared")
                            st.rerun()
    
    st.markdown("---")
    
    # ML Model Training Section
    st.header("🤖 Machine Learning Model Training")
    
    ml_col1, ml_col2 = st.columns([3, 1])
    with ml_col1:
        st.info("Train predictive models using your downloaded datasets")
    with ml_col2:
        if st.button("💾 Save Model", key="save_model_btn", use_container_width=True, disabled=(not downloaded_datasets)):
            if st.session_state.get('trained_model'):
                model_bytes = st.session_state['trained_model'].save_model()
                if model_bytes:
                    st.download_button(
                        label="📥 Download Model",
                        data=model_bytes,
                        file_name="trained_model.pkl",
                        mime="application/octet-stream"
                    )
    
    if downloaded_datasets:
        with st.expander("🎯 Train Model", expanded=False):
            # Step 1: Select Dataset
            st.subheader("Step 1: Select Dataset")
            selected_ds_idx = st.selectbox(
                "Choose a dataset",
                range(len(downloaded_datasets)),
                format_func=lambda i: downloaded_datasets[i]['name'],
                key="ml_dataset_select"
            )
            selected_ds = downloaded_datasets[selected_ds_idx]
            
            # Load and display data
            trainer = ModelTrainer()
            df = trainer.load_data(selected_ds['transfer_info']['downloaded_data'])
            
            if df is not None:
                # Display data summary
                with st.expander("📊 Data Summary", expanded=False):
                    summary = trainer.get_data_summary(df)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📈 Rows", summary['rows'])
                    with col2:
                        st.metric("📋 Columns", summary['columns'])
                    with col3:
                        missing_total = sum(summary['missing_values'].values())
                        st.metric("⚠️ Missing Values", missing_total)
                    
                    st.markdown("**Data Preview:**")
                    st.dataframe(df.head(10), use_container_width=True)
                    
                    st.markdown("**Column Information:**")
                    col_info = pd.DataFrame({
                        'Column': summary['column_names'],
                        'Type': [str(t) for t in summary['dtypes'].values()],
                        'Missing': [summary['missing_values'][c] for c in summary['column_names']]
                    })
                    st.dataframe(col_info, use_container_width=True)
                
                # Step 2: Configure Model
                st.subheader("Step 2: Configure Model")
                
                col_config1, col_config2, col_config3 = st.columns(3)
                
                with col_config1:
                    problem_type = st.selectbox(
                        "Problem Type",
                        ["classification", "regression"],
                        help="Classification for predicting categories, Regression for predicting numbers"
                    )
                
                with col_config2:
                    target_col = st.selectbox(
                        "Target Column (what to predict)",
                        summary['column_names'],
                        help="The column you want to predict"
                    )
                
                with col_config3:
                    model_type = st.selectbox(
                        "Model Type",
                        ["Random Forest", "SVM", "Logistic Regression"] if problem_type == "classification" 
                        else ["Random Forest", "SVM", "Linear Regression"]
                    )
                
                # Step 3: Model Hyperparameters
                st.subheader("Step 3: Hyperparameters")
                
                col_hp1, col_hp2, col_hp3 = st.columns(3)
                
                with col_hp1:
                    test_size = st.slider(
                        "Test Set Size (%)",
                        min_value=10,
                        max_value=50,
                        value=20,
                        help="Percentage of data to use for testing"
                    )
                
                if model_type in ["Random Forest"]:
                    with col_hp2:
                        n_estimators = st.slider(
                            "Number of Trees",
                            min_value=10,
                            max_value=500,
                            value=100,
                            step=10
                        )
                    with col_hp3:
                        max_depth = st.slider(
                            "Max Tree Depth",
                            min_value=3,
                            max_value=30,
                            value=10
                        )
                elif model_type == "SVM":
                    with col_hp2:
                        kernel = st.selectbox("Kernel", ["rbf", "linear", "poly"], key="svm_kernel")
                    with col_hp3:
                        C = st.slider("C (Regularization)", 0.01, 100.0, 1.0, step=0.1, format="%.2f")
                else:  # Logistic Regression or Linear Regression
                    with col_hp2:
                        max_iter = st.slider(
                            "Max Iterations",
                            min_value=100,
                            max_value=5000,
                            value=1000,
                            step=100
                        )
                    col_hp3.empty()
                
                # Step 4: Train Model
                st.subheader("Step 4: Train & Evaluate")
                
                if st.button("🚀 Train Model", use_container_width=True, type="primary"):
                    with st.spinner(f"Training {model_type} model..."):
                        # Prepare data with stratification for classification
                        X_train, X_test, y_train, y_test, X = trainer.prepare_data(
                            df, 
                            target_col,
                            problem_type=problem_type,
                            test_size=test_size/100
                        )
                        
                        if X_train is not None:
                            # Prepare hyperparameters
                            kwargs = {}
                            if model_type == "Random Forest":
                                kwargs = {'n_estimators': n_estimators, 'max_depth': max_depth}
                            elif model_type == "SVM":
                                kwargs = {'kernel': kernel, 'C': C}
                            elif model_type in ["Logistic Regression", "Linear Regression"]:
                                kwargs = {'max_iter': max_iter}
                            
                            # Train model
                            success, y_pred, y_test_actual = trainer.train_model(
                                X_train, X_test, y_train, y_test,
                                model_type, problem_type, **kwargs
                            )
                            
                            if success:
                                # Store model in session state
                                st.session_state.trained_model = trainer
                                st.session_state.model_type = model_type
                                st.session_state.problem_type = problem_type
                                st.session_state.y_pred = y_pred
                                st.session_state.y_test = y_test_actual
                                
                                st.success("✅ Model trained successfully!")
                                st.rerun()
                
                # Display model metrics if trained
                if st.session_state.get('trained_model'):
                    st.subheader("📈 Model Performance")
                    
                    trainer = st.session_state['trained_model']
                    metrics = trainer.metrics
                    
                    # Display metrics
                    if st.session_state.problem_type == 'classification':
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Accuracy", f"{metrics.get('accuracy', 0):.4f}")
                        with col2:
                            st.metric("Precision", f"{metrics.get('precision', 0):.4f}")
                        with col3:
                            st.metric("Recall", f"{metrics.get('recall', 0):.4f}")
                        with col4:
                            st.metric("F1-Score", f"{metrics.get('f1', 0):.4f}")
                        
                        # Visualizations
                        col_viz1, col_viz2 = st.columns(2)
                        
                        with col_viz1:
                            cm_fig = trainer.visualize_confusion_matrix(
                                st.session_state.y_test, 
                                st.session_state.y_pred
                            )
                            if cm_fig:
                                st.pyplot(cm_fig)
                        
                        with col_viz2:
                            # Classification report
                            report = pd.DataFrame(
                                trainer.metrics
                            ).to_frame().T
                            st.write("**Metrics Summary:**")
                            st.dataframe(report, use_container_width=True)
                    
                    else:  # Regression
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("R² Score", f"{metrics.get('r2', 0):.4f}")
                        with col2:
                            st.metric("RMSE", f"{metrics.get('rmse', 0):.4f}")
                        with col3:
                            st.metric("MAE", f"{metrics.get('mae', 0):.4f}")
                        with col4:
                            st.metric("MSE", f"{metrics.get('mse', 0):.4f}")
                        
                        # Visualizations
                        pred_fig = trainer.visualize_predictions(
                            st.session_state.y_test,
                            st.session_state.y_pred
                        )
                        if pred_fig:
                            st.pyplot(pred_fig)
                    
                    # Feature importance if available
                    fi_fig = trainer.visualize_feature_importance(top_n=10)
                    if fi_fig:
                        st.subheader("🔍 Feature Importance")
                        st.pyplot(fi_fig)
                
                # Make predictions on new data
                if st.session_state.get('trained_model'):
                    st.markdown("---")
                    st.subheader("🔮 Make Predictions")
                    
                    trainer = st.session_state['trained_model']
                    
                    with st.expander("Enter Data for Prediction", expanded=False):
                        # Create input form for all features
                        input_data = {}
                        
                        cols = st.columns(3)
                        for idx, feature in enumerate(trainer.feature_names):
                            with cols[idx % 3]:
                                if feature in trainer.encoders and feature != 'target':
                                    # Categorical feature
                                    options = trainer.encoders[feature].classes_
                                    input_data[feature] = st.selectbox(
                                        f"{feature}",
                                        options,
                                        key=f"pred_{feature}"
                                    )
                                else:
                                    # Numeric feature
                                    input_data[feature] = st.number_input(
                                        f"{feature}",
                                        key=f"pred_{feature}"
                                    )
                        
                        if st.button("🎯 Predict", use_container_width=True):
                            success, prediction, confidence = trainer.predict(input_data)
                            
                            if success:
                                col_pred1, col_pred2 = st.columns([3, 1])
                                with col_pred1:
                                    st.success(f"**Prediction: {prediction}**")
                                with col_pred2:
                                    if confidence:
                                        st.info(f"Confidence: {confidence:.2%}")
                            else:
                                st.error(f"Prediction failed: {prediction}")
    else:
        st.info("📭 No datasets downloaded yet. Download a dataset to train a model.")
    
    st.markdown("---")
    
    # Model Inference Section
    st.header("🔮 Model Inference & Prediction")
    
    st.info("Use trained models to make predictions on new data")
    
    # Check if we have trained models or uploaded models
    inference_col1, inference_col2 = st.columns([2, 1])
    
    with inference_col2:
        inference_option = st.radio(
            "Model Source",
            ["Use Trained Model", "Upload Model File"],
            horizontal=True,
            label_visibility="collapsed"
        )
    
    inference_trainer = None
    
    if inference_option == "Use Trained Model":
        if st.session_state.get('trained_model'):
            with inference_col1:
                st.success("✅ Trained model available")
            inference_trainer = st.session_state['trained_model']
        else:
            with inference_col1:
                st.warning("⚠️ No trained model available yet")
            st.info("💡 Train a model first in the 'Machine Learning Model Training' section above")
    
    else:  # Upload Model File
        with inference_col1:
            st.caption("Upload a previously saved model file")
        
        uploaded_model = st.file_uploader(
            "Choose model file",
            type=["pkl", "pickle"],
            help="Select a pickled model file (.pkl or .pickle)"
        )
        
        if uploaded_model is not None:
            with st.spinner("Loading model..."):
                try:
                    inference_trainer = pickle.load(uploaded_model)
                    st.session_state['inference_trainer'] = inference_trainer
                    st.success("✅ Model loaded successfully!")
                except Exception as e:
                    st.error(f"❌ Error loading model: {str(e)}")
                    inference_trainer = None
        elif 'inference_trainer' in st.session_state:
            inference_trainer = st.session_state['inference_trainer']
    
    # Model Inference Interface
    if inference_trainer:
        with st.expander("📊 Model Information", expanded=True):
            info_col1, info_col2, info_col3 = st.columns(3)
            
            with info_col1:
                st.metric("🎯 Model Type", "Classification" if hasattr(inference_trainer, 'metrics') and 'accuracy' in inference_trainer.metrics else "Regression")
            
            with info_col2:
                feature_count = len(inference_trainer.feature_names) if hasattr(inference_trainer, 'feature_names') else 0
                st.metric("📌 Features", feature_count)
            
            with info_col3:
                metrics = inference_trainer.metrics if hasattr(inference_trainer, 'metrics') else {}
                if 'accuracy' in metrics:
                    st.metric("📈 Accuracy", f"{metrics['accuracy']:.4f}")
                elif 'r2' in metrics:
                    st.metric("📈 R² Score", f"{metrics['r2']:.4f}")
                else:
                    st.metric("📈 Status", "Ready")
            
            # Display feature names
            if hasattr(inference_trainer, 'feature_names'):
                st.markdown("**Input Features:**")
                features_df = pd.DataFrame({
                    'Feature': inference_trainer.feature_names,
                    'Type': ['Categorical' if (hasattr(inference_trainer, 'encoders') and f in inference_trainer.encoders) else 'Numeric' for f in inference_trainer.feature_names]
                })
                st.dataframe(features_df, use_container_width=True, hide_index=True)
        
        # Prediction Interface
        st.subheader("🎯 Make Predictions")
        
        # Toggle between input methods
        input_method = st.radio(
            "Input Method",
            ["📝 Manual Input", "📋 Paste CSV String"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        if input_method == "📋 Paste CSV String":
            # CSV String Input
            st.markdown("**Paste data as comma-separated values (CSV format):**")
            csv_string = st.text_area(
                "CSV Input",
                placeholder="5729,164,3,-3.71378,40.3518,0,3413,17,177.47,290.21,5.74,16.65,0,0,0,20251211,1765521373,4",
                height=60,
                label_visibility="collapsed",
                help="Paste a single row of comma-separated values matching the feature order"
            )
            
            if st.button("🚀 Predict from CSV", use_container_width=True, type="primary"):
                try:
                    # Parse CSV string
                    values = [v.strip() for v in csv_string.split(',')]
                    
                    if len(values) != len(inference_trainer.feature_names):
                        st.error(f"❌ Expected {len(inference_trainer.feature_names)} values, got {len(values)}")
                        st.info(f"Expected features in order: {', '.join(inference_trainer.feature_names)}")
                    else:
                        # Create input data dictionary
                        input_data = {}
                        for idx, feature in enumerate(inference_trainer.feature_names):
                            try:
                                # Try to convert to appropriate type
                                value = values[idx]
                                if hasattr(inference_trainer, 'encoders') and feature in inference_trainer.encoders:
                                    # Keep as string for encoding
                                    input_data[feature] = value
                                else:
                                    # Convert to numeric
                                    if '.' in value:
                                        input_data[feature] = float(value)
                                    else:
                                        input_data[feature] = int(value)
                            except ValueError:
                                st.error(f"❌ Could not parse value '{value}' for feature '{feature}'")
                                st.stop()
                        
                        with st.spinner("🔄 Making prediction..."):
                            success, prediction, confidence = inference_trainer.predict(input_data)
                            
                            if success:
                                st.markdown("---")
                                
                                # Display prediction result
                                result_col1, result_col2, result_col3 = st.columns([2, 1, 1])
                                
                                with result_col1:
                                    st.success(f"### ✅ Prediction Result")
                                    st.markdown(f"**Predicted Value:** `{prediction}`")
                                
                                with result_col2:
                                    if confidence:
                                        confidence_pct = confidence * 100
                                        if confidence_pct >= 80:
                                            st.success(f"**Confidence**\n{confidence_pct:.1f}%")
                                        elif confidence_pct >= 60:
                                            st.warning(f"**Confidence**\n{confidence_pct:.1f}%")
                                        else:
                                            st.error(f"**Confidence**\n{confidence_pct:.1f}%")
                                
                                with result_col3:
                                    st.info(f"**Status**\nSuccess")
                                
                                # Display input summary
                                st.markdown("**Input Summary:**")
                                input_df = pd.DataFrame({
                                    'Feature': list(input_data.keys()),
                                    'Value': list(input_data.values())
                                })
                                st.dataframe(input_df, use_container_width=True, hide_index=True)
                                
                                # Download prediction as CSV
                                output_data = {**input_data, 'prediction': prediction}
                                if confidence:
                                    output_data['confidence'] = confidence
                                
                                csv_output = pd.DataFrame([output_data]).to_csv(index=False)
                                st.download_button(
                                    label="📥 Download Prediction (CSV)",
                                    data=csv_output,
                                    file_name="prediction.csv",
                                    mime="text/csv",
                                    use_container_width=True
                                )
                            else:
                                st.error(f"❌ Prediction failed: {prediction}")
                
                except Exception as e:
                    st.error(f"❌ Error parsing CSV: {str(e)}")
        
        else:
            # Manual Input Form
            with st.form("prediction_form", clear_on_submit=False):
                st.markdown("**Enter data for prediction:**")
                
                input_data = {}
                cols = st.columns(3)
                
                # Create input fields for each feature
                for idx, feature in enumerate(inference_trainer.feature_names):
                    with cols[idx % 3]:
                        if hasattr(inference_trainer, 'encoders') and feature in inference_trainer.encoders:
                            # Categorical feature with dropdown
                            options = inference_trainer.encoders[feature].classes_
                            input_data[feature] = st.selectbox(
                                f"📌 {feature}",
                                options,
                                key=f"inference_pred_{feature}"
                            )
                        else:
                            # Numeric feature with number input
                            input_data[feature] = st.number_input(
                                f"🔢 {feature}",
                                key=f"inference_pred_{feature}"
                            )
                
                st.markdown("---")
                predict_button = st.form_submit_button("🚀 Predict", use_container_width=True, type="primary")
                
                if predict_button:
                    with st.spinner("🔄 Making prediction..."):
                        success, prediction, confidence = inference_trainer.predict(input_data)
                        
                        if success:
                            st.markdown("---")
                            
                            # Display prediction result
                            result_col1, result_col2, result_col3 = st.columns([2, 1, 1])
                            
                            with result_col1:
                                st.success(f"### ✅ Prediction Result")
                                st.markdown(f"**Predicted Value:** `{prediction}`")
                            
                            with result_col2:
                                if confidence:
                                    confidence_pct = confidence * 100
                                    if confidence_pct >= 80:
                                        st.success(f"**Confidence**\n{confidence_pct:.1f}%")
                                    elif confidence_pct >= 60:
                                        st.warning(f"**Confidence**\n{confidence_pct:.1f}%")
                                    else:
                                        st.error(f"**Confidence**\n{confidence_pct:.1f}%")
                            
                            with result_col3:
                                st.info(f"**Status**\nSuccess")
                            
                            # Display input summary
                            st.markdown("**Input Summary:**")
                            input_df = pd.DataFrame({
                                'Feature': list(input_data.keys()),
                                'Value': list(input_data.values())
                            })
                            st.dataframe(input_df, use_container_width=True, hide_index=True)
                            
                            # Download prediction as CSV
                            output_data = {**input_data, 'prediction': prediction}
                            if confidence:
                                output_data['confidence'] = confidence
                            
                            csv_output = pd.DataFrame([output_data]).to_csv(index=False)
                            col_export1, col_export2 = st.columns([1, 1])
                            with col_export1:
                                st.download_button(
                                    label="📥 Download Prediction (CSV)",
                                    data=csv_output,
                                    file_name="prediction.csv",
                                    mime="text/csv",
                                    use_container_width=True
                                )
                            with col_export2:
                                st.button(
                                    label="🔄 Make Another Prediction",
                                    use_container_width=True,
                                    key="another_pred"
                                )
                        else:
                            st.error(f"❌ Prediction failed: {prediction}")
        
        # Batch Prediction Section
        st.markdown("---")
        st.subheader("📊 Batch Prediction")
        
        with st.expander("Upload CSV for batch predictions", expanded=False):
            st.markdown("Upload a CSV file with multiple samples for bulk prediction")
            
            batch_file = st.file_uploader(
                "Choose CSV file",
                type=["csv"],
                key="batch_prediction_file",
                help="CSV file with columns matching the model's input features"
            )
            
            if batch_file is not None:
                batch_df = pd.read_csv(batch_file)
                
                st.markdown(f"**Uploaded file:** {batch_file.name} ({len(batch_df)} rows)")
                
                with st.expander("Preview data", expanded=False):
                    st.dataframe(batch_df.head(10), use_container_width=True)
                
                if st.button("🚀 Run Batch Prediction", use_container_width=True):
                    with st.spinner("Processing batch predictions..."):
                        progress_bar = st.progress(0)
                        predictions_list = []
                        
                        for idx, row in enumerate(batch_df.iterrows()):
                            row_data = row[1].to_dict()
                            success, pred, conf = inference_trainer.predict(row_data)
                            
                            if success:
                                predictions_list.append({
                                    'prediction': pred,
                                    'confidence': conf if conf else None
                                })
                            else:
                                predictions_list.append({
                                    'prediction': 'ERROR',
                                    'confidence': None
                                })
                            
                            progress_bar.progress((idx + 1) / len(batch_df))
                        
                        # Create results dataframe
                        results_df = pd.concat([
                            batch_df.reset_index(drop=True),
                            pd.DataFrame(predictions_list)
                        ], axis=1)
                        
                        st.success("✅ Batch prediction complete!")
                        
                        # Display results
                        st.markdown("**Results:**")
                        st.dataframe(results_df, use_container_width=True)
                        
                        # Download results
                        csv_results = results_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Results (CSV)",
                            data=csv_results,
                            file_name="batch_predictions.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
    
    else:
        st.info("💡 No model available. Train a model or upload a saved model file to make predictions.")
    
    st.markdown("---")
    
    # Catalog section
    st.header("📚 Provider Catalog")
    
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.info("Browse available datasets from the provider connector")
    with col2:
        if st.button("🔄 Refresh Catalog", use_container_width=True):
            st.session_state.catalog = None
    with col3:
        if st.button("🗑️ Clear All", use_container_width=True):
            # Terminate all active transfers
            if 'transfers' in st.session_state:
                for dataset_id, transfer_info in st.session_state.transfers.items():
                    if transfer_info.get('status') in ['STARTED', 'REQUESTED']:
                        edc_client.terminate_transfer(transfer_info['transfer_id'])
            # Clear session state
            st.session_state.negotiations = {}
            st.session_state.transfers = {}
            st.success("✅ All sessions cleared")
            st.rerun()
    
    # Fetch catalog if not cached
    if st.session_state.catalog is None:
        with st.spinner("Fetching catalog from provider..."):
            catalog = edc_client.get_catalog()
            if catalog:
                st.session_state.catalog = edc_client.parse_catalog_datasets(catalog)
            else:
                st.error("Failed to fetch catalog. Please check connectivity.")
                return
    
    # Display catalog
    datasets = st.session_state.catalog
    
    if not datasets:
        st.warning("No datasets found in the catalog")
        return
    
    st.success(f"Found **{len(datasets)}** dataset(s)")
    
    # Display datasets in cards
    for idx, dataset in enumerate(datasets):
        with st.expander(f"📦 {dataset['name']}", expanded=(idx == 0)):
            # Basic information in two columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**ID:** `{dataset['id']}`")
                st.markdown(f"**Name:** {dataset['name']}")
                if dataset.get('filename'):
                    st.markdown(f"**📄 Filename:** `{dataset['filename']}`")
                st.markdown(f"**Content-Type:** {dataset.get('contentType', 'N/A')}")
                st.markdown(f"**Version:** {dataset['version']}")
                st.markdown(f"**Asset type:** {dataset.get('assetType', 'Unknown')}")
            
            with col2:
                st.markdown(f"**Keywords:** {dataset['keywords']}")
                st.markdown(f"**Byte size:** {dataset['byteSize']}")
                st.markdown(f"**File format:** {dataset['format']}")
                st.markdown(f"**Provider:** `{dataset['participantId']}`")
                formats_list = dataset.get('distributionFormats', [])
                if isinstance(formats_list, list):
                    formats_str = ', '.join(formats_list) if formats_list else 'N/A'
                else:
                    formats_str = str(formats_list)
                st.markdown(f"**Distribution Types:** {formats_str}")
            
            # Descriptions
            st.markdown("---")
            st.markdown(f"**Short description:** {dataset.get('shortDescription', 'No description')}")
            
            st.markdown("**Description:**")
            desc_html = dataset.get('description_html', dataset['description'])
            if desc_html and desc_html.startswith('<'):
                st.markdown(desc_html, unsafe_allow_html=True)
            else:
                st.write(desc_html if desc_html else 'No description')
            
            # Technical details
            st.markdown("---")
            st.markdown(f"**Protocol Endpoint:** `{dataset['endpoint']}`")
            
            if dataset.get('offerId'):
                st.markdown(f"**Contract Offer ID:** `{dataset['offerId']}`")
            
            # Action buttons
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("🤝 Negotiate", key=f"negotiate_{idx}", use_container_width=True):
                    if not dataset.get('offerId'):
                        st.error("No offer ID available for this dataset")
                    else:
                        with st.spinner("Initiating contract negotiation..."):
                            negotiation_id = edc_client.initiate_negotiation(
                                offer_id=dataset['offerId'],
                                asset_id=dataset['id'],
                                provider_endpoint=dataset['endpoint'],
                                offer=dataset.get('offer', {})
                            )
                            
                            if negotiation_id:
                                # Store negotiation info in session state
                                if 'negotiations' not in st.session_state:
                                    st.session_state.negotiations = {}
                                st.session_state.negotiations[dataset['id']] = {
                                    'negotiation_id': negotiation_id,
                                    'status': 'INITIATED'
                                }
            
            with col2:
                # Check if negotiation exists for this dataset
                has_negotiation = ('negotiations' in st.session_state and 
                                 dataset['id'] in st.session_state.negotiations)
                
                if st.button("🔄 Check Status", key=f"status_{idx}", 
                           use_container_width=True, disabled=not has_negotiation):
                    if has_negotiation:
                        neg_id = st.session_state.negotiations[dataset['id']]['negotiation_id']
                        with st.spinner("Checking negotiation status..."):
                            status = edc_client.check_negotiation_status(neg_id)
                            if status:
                                state = status.get('state', status.get('edc:state', 'UNKNOWN'))
                                st.info(f"Status: {state}")
                                st.session_state.negotiations[dataset['id']]['status'] = state
                                st.session_state.negotiations[dataset['id']]['data'] = status
                                
                                # Extract contract agreement ID if finalized
                                if state == 'FINALIZED':
                                    contract_id = status.get('contractAgreementId', status.get('edc:contractAgreementId'))
                                    if contract_id:
                                        st.session_state.negotiations[dataset['id']]['contract_agreement_id'] = contract_id
                                        st.success(f"✅ Contract Agreement ID: {contract_id}")
            
            with col3:
                # Enable transfer if negotiation is finalized
                has_agreement = (has_negotiation and 
                               st.session_state.negotiations.get(dataset['id'], {}).get('status') == 'FINALIZED' and
                               'contract_agreement_id' in st.session_state.negotiations.get(dataset['id'], {}))
                
                if st.button("📥 New Transfer", key=f"transfer_{idx}", use_container_width=True, disabled=not has_agreement):
                    if has_agreement:
                        contract_id = st.session_state.negotiations[dataset['id']]['contract_agreement_id']
                        with st.spinner("Initiating transfer..."):
                            transfer_id = edc_client.initiate_transfer(
                                contract_agreement_id=contract_id,
                                asset_id=dataset['id'],
                                provider_endpoint=dataset['endpoint']
                            )
                            
                            if transfer_id:
                                # Store transfer info
                                if 'transfers' not in st.session_state:
                                    st.session_state.transfers = {}
                                st.session_state.transfers[dataset['id']] = {
                                    'transfer_id': transfer_id,
                                    'status': 'INITIATED'
                                }
                                st.success(f"✅ Transfer initiated: {transfer_id}")
            
            with col4:
                # Show full metadata button
                with st.popover("🔍 Full Metadata"):
                    st.json(dataset['properties'])
            
            # Second row of buttons for transfer operations
            if 'negotiations' in st.session_state and dataset['id'] in st.session_state.negotiations:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Check transfer status
                    has_transfer = ('transfers' in st.session_state and 
                                  dataset['id'] in st.session_state.transfers)
                    
                    if st.button("🔍 Transfer Status", key=f"transfer_status_{idx}", 
                               use_container_width=True, disabled=not has_transfer):
                        if has_transfer:
                            transfer_id = st.session_state.transfers[dataset['id']]['transfer_id']
                            with st.spinner("Checking transfer status..."):
                                transfer_status = edc_client.check_transfer_status(transfer_id)
                                if transfer_status:
                                    state = transfer_status.get('state', transfer_status.get('edc:state', 'UNKNOWN'))
                                    st.info(f"Transfer Status: {state}")
                                    st.session_state.transfers[dataset['id']]['status'] = state
                                    st.session_state.transfers[dataset['id']]['data'] = transfer_status
                                    
                                    # Get EDR if transfer is started/completed  
                                    if state in ['STARTED', 'COMPLETED']:
                                        edr_data = edc_client.get_edr(transfer_id)
                                        
                                        if edr_data:
                                            with st.expander("Debug: EDR Data"):
                                                st.json(edr_data)
                                            
                                            # Extract endpoint and auth from EDR
                                            endpoint = (edr_data.get('endpoint') or 
                                                      edr_data.get('edc:endpoint') or
                                                      edr_data.get('baseUrl'))
                                            auth_key = edr_data.get('authKey', edr_data.get('edc:authKey', 'Authorization'))
                                            auth_code = (edr_data.get('authCode') or 
                                                       edr_data.get('edc:authCode') or
                                                       edr_data.get('authorization'))
                                            
                                            if endpoint and auth_code:
                                                st.session_state.transfers[dataset['id']]['edr_endpoint'] = endpoint
                                                st.session_state.transfers[dataset['id']]['edr_auth_key'] = auth_key
                                                st.session_state.transfers[dataset['id']]['edr_auth_code'] = auth_code
                                                st.session_state.transfers[dataset['id']]['edr_data'] = edr_data
                                                st.success(f"✅ EDR obtained! Endpoint ready.")
                                            else:
                                                st.warning(f"⚠️ EDR incomplete - endpoint: {bool(endpoint)}, auth: {bool(auth_code)}")
                                    
                                    # Show full transfer details
                                    with st.expander("Transfer details"):
                                        st.json(transfer_status)
            
            # Show negotiation status if exists
            if 'negotiations' in st.session_state and dataset['id'] in st.session_state.negotiations:
                neg_info = st.session_state.negotiations[dataset['id']]
                st.info(f"📋 Negotiation ID: `{neg_info['negotiation_id']}` | Status: **{neg_info['status']}**")
            
            # Show transfer status if exists
            if 'transfers' in st.session_state and dataset['id'] in st.session_state.transfers:
                transfer_info = st.session_state.transfers[dataset['id']]
                col_status, col_stop = st.columns([3, 1])
                with col_status:
                    st.info(f"📦 Transfer ID: `{transfer_info['transfer_id']}` | Status: **{transfer_info.get('status', 'UNKNOWN')}**")
                with col_stop:
                    if transfer_info.get('status') in ['STARTED', 'REQUESTED']:
                        if st.button("🛑 Stop", key=f"stop_{dataset['id']}"):
                            if edc_client.terminate_transfer(transfer_info['transfer_id']):
                                st.session_state.transfers[dataset['id']]['status'] = 'TERMINATED'
                                st.rerun()
                
                # Show download button if EDR is available
                if 'edr_endpoint' in transfer_info:
                    if st.button(f"⬇️ Download Data", key=f"download_{dataset['id']}"):
                        with st.spinner("Downloading data..."):
                            data = edc_client.download_data(
                                edr_endpoint=transfer_info['edr_endpoint'],
                                edr_auth_key=transfer_info['edr_auth_key'],
                                edr_auth_code=transfer_info['edr_auth_code'],
                                asset_id=dataset['id'],
                                edr_data=transfer_info.get('edr_data', {})
                            )
                            
                            if data:
                                # Store downloaded data in session state
                                st.session_state.transfers[dataset['id']]['downloaded_data'] = data
                                
                                col_save, col_process = st.columns(2)
                                with col_save:
                                    # Offer download to user
                                    st.download_button(
                                        label="💾 Save File",
                                        data=data,
                                        file_name=f"{dataset['name']}.{dataset.get('format', 'data')}",
                                        mime="application/octet-stream",
                                        use_container_width=True
                                    )
                                with col_process:
                                    if st.button("🎨 Process with TINTOlib", key=f"tinto_{dataset['id']}", use_container_width=True):
                                        st.session_state.transfers[dataset['id']]['show_tinto'] = True
                                        st.rerun()
                    
                    # Show TINTOlib processing section if requested
                    if transfer_info.get('show_tinto') and transfer_info.get('downloaded_data'):
                        st.markdown("---")
                        st.subheader("🎨 TINTOlib: Convert to Synthetic Images")
                        
                        with st.expander("⚙️ TINTOlib Configuration", expanded=True):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                method = st.selectbox("Method", ["TINTO"], key=f"method_{dataset['id']}")
                                algorithm = st.selectbox("Algorithm", ["t-SNE", "PCA"], key=f"algo_{dataset['id']}")
                            with col2:
                                pixels = st.slider("Pixels", 10, 50, 20, key=f"pixels_{dataset['id']}")
                                steps = st.slider("Steps", 1, 10, 5, key=f"steps_{dataset['id']}")
                            with col3:
                                blur = st.checkbox("Apply Blur", value=True, key=f"blur_{dataset['id']}")
                                problem = st.selectbox("Problem Type", ["supervised", "unsupervised"], key=f"problem_{dataset['id']}")
                        
                        if st.button("🚀 Generate Images", key=f"gen_{dataset['id']}"):
                            processor = TINTOProcessor()
                            
                            images = processor.process_data(
                                csv_data=transfer_info['downloaded_data'],
                                method=method,
                                algorithm=algorithm,
                                pixels=pixels,
                                steps=steps,
                                blur=blur,
                                problem=problem
                            )
                            
                            if images:
                                st.session_state.transfers[dataset['id']]['tinto_images'] = images
                                processor.display_images(images, max_display=12)
                                st.success("✨ TINTOlib processing complete!")
                                
                                # Option to cleanup
                                if st.button("🗑️ Clear Images", key=f"clear_tinto_{dataset['id']}"):
                                    processor.cleanup()
                                    if 'tinto_images' in st.session_state.transfers[dataset['id']]:
                                        del st.session_state.transfers[dataset['id']]['tinto_images']
                                    st.success("Images cleared")
                                    st.rerun()
                            else:
                                st.error("Failed to generate images")
                        
                        # Display previously generated images if they exist
                        elif 'tinto_images' in transfer_info:
                            processor = TINTOProcessor()
                            processor.display_images(transfer_info['tinto_images'], max_display=12)
    
    st.markdown("---")
    st.caption("🔹 Next steps: Click 'Request Data' to initiate automatic negotiation and transfer")


def main():
    """Main application entry point"""
    if not st.session_state.authenticated:
        login_page()
    else:
        catalog_page()


if __name__ == "__main__":
    main()
