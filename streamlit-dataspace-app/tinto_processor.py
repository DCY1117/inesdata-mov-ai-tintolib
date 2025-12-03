"""
TINTOlib Data Processor
Converts downloaded CSV datasets into synthetic images
"""

import streamlit as st
import pandas as pd
import io
from pathlib import Path
import tempfile
import shutil
from PIL import Image


class TINTOProcessor:
    """
    Processes tabular data using TINTOlib to generate synthetic images
    """
    
    def __init__(self):
        self.temp_dir = None
        self.output_dir = None
    
    def process_data(self, csv_data: bytes, method: str = "TINTO", **kwargs):
        """
        Process CSV data and convert to synthetic images using TINTOlib
        
        Args:
            csv_data: Raw CSV file data as bytes
            method: TINTOlib method to use (TINTO, IGTD, REFINED, BarGraph, etc.)
            **kwargs: Additional parameters for the specific method
            
        Returns:
            List of generated image paths, or None if failed
        """
        try:
            # Import appropriate method
            try:
                if method == "TINTO":
                    from TINTOlib.tinto import TINTO as ModelClass
                elif method == "IGTD":
                    from TINTOlib.igtd import IGTD as ModelClass
                elif method == "REFINED":
                    from TINTOlib.refined import REFINED as ModelClass
                elif method == "BarGraph":
                    from TINTOlib.barGraph import BarGraph as ModelClass
                elif method == "DistanceMatrix":
                    from TINTOlib.distanceMatrix import DistanceMatrix as ModelClass
                elif method == "Combination":
                    from TINTOlib.combination import Combination as ModelClass
                elif method == "SuperTML":
                    from TINTOlib.supertml import SuperTML as ModelClass
                elif method == "FeatureWrap":
                    from TINTOlib.featureWrap import FeatureWrap as ModelClass
                elif method == "BIE":
                    from TINTOlib.bie import BIE as ModelClass
                else:
                    from TINTOlib.tinto import TINTO as ModelClass
            except ImportError as e:
                st.error(f"❌ TINTOlib not installed: {str(e)}")
                st.info("📦 Install TINTOlib (without REFINED method):")
                st.code("pip install --no-deps TINTOlib && pip install numpy pandas scikit-learn matplotlib Pillow seaborn")
                st.warning("⚠️ Note: REFINED method requires mpi4py and MPI libraries (not included)")
                return None
            
            # Create temporary directories
            self.temp_dir = tempfile.mkdtemp()
            self.output_dir = tempfile.mkdtemp()
            
            # Save CSV to temp file
            csv_path = Path(self.temp_dir) / "data.csv"
            with open(csv_path, 'wb') as f:
                f.write(csv_data)
            
            # Verify CSV can be read
            df = pd.read_csv(csv_path)
            st.info(f"📊 Dataset loaded: {len(df)} rows, {len(df.columns)} columns")
            st.info(f"🔧 Using method: {method}")
            
            # Display first few rows
            with st.expander("Preview Original Data"):
                st.dataframe(df.head())
            
            # Preprocess: encode categorical target column if needed
            problem_type = kwargs.get('problem', 'supervised')
            if problem_type in ['supervised', 'classification']:
                # Check if last column (target) is categorical
                last_col = df.columns[-1]
                if df[last_col].dtype == 'object' or df[last_col].dtype.name == 'category':
                    st.info(f"🔄 Encoding categorical target column: '{last_col}'")
                    from sklearn.preprocessing import LabelEncoder
                    le = LabelEncoder()
                    df[last_col] = le.fit_transform(df[last_col])
                    
                    # Show mapping
                    mapping = {label: idx for idx, label in enumerate(le.classes_)}
                    st.info(f"📋 Label mapping: {mapping}")
                    
                    # Save preprocessed data
                    df.to_csv(csv_path, index=False)
                    
                    with st.expander("Preview Preprocessed Data"):
                        st.dataframe(df.head())
            
            # Initialize TINTOlib model with appropriate parameters
            model = ModelClass(**kwargs)
            
            # Generate synthetic images
            st.info("🎨 Generating synthetic images...")
            progress_bar = st.progress(0)
            
            model.fit_transform(str(csv_path), str(self.output_dir))
            
            progress_bar.progress(100)
            
            # Get generated images
            image_files = list(Path(self.output_dir).glob("**/*.png"))
            
            if not image_files:
                st.warning("No images were generated. Check if the dataset format is correct.")
                return None
            
            st.success(f"✅ Generated {len(image_files)} synthetic images!")
            
            return [str(img) for img in image_files]
            
        except ImportError as e:
            st.error(f"❌ TINTOlib not installed: {str(e)}")
            st.info("Install with: pip install TINTOlib")
            return None
        except Exception as e:
            st.error(f"❌ Error processing data: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            return None
    
    def display_images(self, image_paths: list, max_display: int = 10):
        """
        Display generated synthetic images in a grid
        
        Args:
            image_paths: List of image file paths
            max_display: Maximum number of images to display
        """
        if not image_paths:
            st.warning("No images to display")
            return
        
        st.subheader("🖼️ Generated Synthetic Images")
        
        # Display images in grid with zoom
        cols_per_row = 4
        num_to_display = min(len(image_paths), max_display)
        
        # Add zoom control
        zoom_factor = st.slider("🔍 Image Zoom", 1, 10, 4, help="Adjust image display size")
        
        for i in range(0, num_to_display, cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                idx = i + j
                if idx < num_to_display:
                    with col:
                        try:
                            img = Image.open(image_paths[idx])
                            # Resize image for better visibility
                            width, height = img.size
                            new_size = (width * zoom_factor, height * zoom_factor)
                            img_resized = img.resize(new_size, Image.Resampling.NEAREST)
                            st.image(img_resized, caption=f"Image {idx+1}", use_container_width=True)
                        except Exception as e:
                            st.error(f"Error loading image: {e}")
        
        if len(image_paths) > max_display:
            st.info(f"Showing {max_display} of {len(image_paths)} images")
        
        # Add download button for all images
        zip_data = self.create_zip_archive(image_paths)
        if zip_data:
            st.download_button(
                label="📦 Download All Images as ZIP",
                data=zip_data,
                file_name="tinto_synthetic_images.zip",
                mime="application/zip",
                use_container_width=True
            )
    
    def create_zip_archive(self, image_paths: list):
        """
        Create a ZIP archive of all generated images with folder structure
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            Bytes of the ZIP file
        """
        try:
            import zipfile
            import io
            
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for img_path in image_paths:
                    # Get the relative path from output_dir to maintain folder structure
                    img_path_obj = Path(img_path)
                    if self.output_dir:
                        relative_path = img_path_obj.relative_to(Path(self.output_dir))
                    else:
                        relative_path = img_path_obj.name
                    
                    # Add file to zip with its folder structure
                    zip_file.write(img_path, arcname=str(relative_path))
            
            zip_buffer.seek(0)
            return zip_buffer.getvalue()
            
        except Exception as e:
            st.error(f"Error creating ZIP: {e}")
            return None
    
    def cleanup(self):
        """Clean up temporary directories"""
        try:
            if self.temp_dir and Path(self.temp_dir).exists():
                shutil.rmtree(self.temp_dir)
            if self.output_dir and Path(self.output_dir).exists():
                shutil.rmtree(self.output_dir)
        except Exception as e:
            st.warning(f"Could not clean up temp files: {e}")
