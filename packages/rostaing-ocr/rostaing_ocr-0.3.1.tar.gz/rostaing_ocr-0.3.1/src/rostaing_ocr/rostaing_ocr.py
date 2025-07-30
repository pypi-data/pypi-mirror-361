import os
import base64
import fitz  # PyMuPDF
import re
from typing import List, Union, Optional, Dict
import io
# 'numpy' est une dépendance de doctr, donc il sera disponible
import numpy as np 

# Import pour Doctr (remplace EasyOCR)
try:
    from doctr.io import DocumentFile
    from doctr.models import ocr_predictor
    DOCTR_AVAILABLE = True
except ImportError:
    DOCTR_AVAILABLE = False


class RostaingOCR:
    """
    Classe d'extraction qui respecte l'ordre vertical (de haut en bas) du contenu
    sur une page PDF, en mélangeant correctement le texte et le contenu des images.

    - Utilise le moteur OCR 'doctr' pour une extraction rapide et précise des documents scannés.
    - Traite chaque page de PDF comme une image pour une analyse de mise en page robuste.
    - L'extraction est lancée dès l'initialisation.

    Utilisation :
        # La langue n'est plus un paramètre actif pour le modèle par défaut, car il est multilingue.
        extractor = RostaingExtractor("document_scanne.pdf")
        print(extractor)
    """

    SUPPORTED_IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff']

    def __init__(self,
                 input_path_or_paths: Union[str, List[str]],
                 output_basename: str = "output",
                 print_to_console: bool = False,
                 save_images_externally: bool = True,
                 image_dpi: int = 300,
                 perform_ocr: bool = True,
                 # CORRECTION: Ce paramètre est conservé pour la compatibilité de l'interface,
                 # mais le modèle par défaut de doctr est multilingue (fr/en inclus).
                 ocr_lang: List[str] = ['fr', 'en']):
        """
        Initialise et lance immédiatement l'extraction.
        """
        if isinstance(input_path_or_paths, str):
            self.input_paths = [input_path_or_paths]
        else:
            self.input_paths = input_path_or_paths

        self.output_basename = output_basename
        self.output_md_path = f"{self.output_basename}.md"
        self.output_txt_path = f"{self.output_basename}.txt"
        
        self.save_images_externally = save_images_externally
        self.image_output_dir = f"{self.output_basename}_images"
        self.image_dpi = image_dpi
        self.print_to_console = print_to_console
        
        self.perform_ocr = perform_ocr
        self.ocr_lang = ocr_lang
        self.ocr_predictor = None
        
        if self.perform_ocr and not DOCTR_AVAILABLE:
            print("WARNING: 'python-doctr' is not installed. OCR is disabled.")
            print("Please install it using: pip install 'python-doctr[torch]'")
            self.perform_ocr = False

        self.results: Dict[str, Optional[str]] = {}
        self._run_extraction()

    def _initialize_ocr_reader(self):
        """Initialise le prédicteur Doctr une seule fois si nécessaire."""
        if self.ocr_predictor is None and self.perform_ocr:
            print("\nInitializing OCR engine...")
            # CORRECTION : On charge le modèle pré-entraîné standard.
            # Il est multilingue et gère la détection d'orientation, ce qui est parfait.
            self.ocr_predictor = ocr_predictor(
                pretrained=True,
                detect_orientation=True
            )
            print("OCR engine ready.")

    def _run_extraction(self):
        """Logique principale d'extraction."""
        print(f"\nStarting RostaingOCR extraction...")
        
        if self.save_images_externally and not os.path.exists(self.image_output_dir):
            os.makedirs(self.image_output_dir)
            print(f"Image folder created: '{self.image_output_dir}'")

        all_final_content = []
        for i, file_path in enumerate(self.input_paths):
            extracted_content = ""
            try:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"The file '{file_path}' does not exist.")

                print(f"\n--- Processing {os.path.basename(file_path)} ({i+1}/{len(self.input_paths)}) ---")
                extracted_content = self._extract_content_from_single_file(file_path)
                
                if extracted_content:
                    content_with_header = f"# Content of: {os.path.basename(file_path)}\n\n{extracted_content}"
                    all_final_content.append(content_with_header)
                    print(f"--- SUCCESS for '{os.path.basename(file_path)}' ---")
                    
                    if self.print_to_console:
                        self._print_result_to_console(os.path.basename(file_path), extracted_content)
                else:
                    print(f"--- FAILURE (no content found) for '{os.path.basename(file_path)}' ---")

            except Exception as e:
                import traceback
                print(f"--- FATAL ERROR for '{os.path.basename(file_path)}': {e} ---")
                traceback.print_exc()
                extracted_content = f"[FATAL ERROR during the processing of '{file_path}': {e}]"
            
            finally:
                self.results[file_path] = extracted_content


        if all_final_content:
            final_output_string = "\n\n===\n\n".join(all_final_content)
            self._save_outputs(final_output_string)
        
        print("\nProcessing complete.")

    def _get_image_markdown(self, image_bytes: bytes, alt_text: str, image_format: str, image_filename: str) -> str:
        """Génère le markdown pour une image, soit en la sauvegardant, soit en l'intégrant en base64."""
        if self.save_images_externally:
            image_path = os.path.join(self.image_output_dir, image_filename)
            with open(image_path, "wb") as f: f.write(image_bytes)
            relative_path = os.path.join(os.path.basename(self.image_output_dir), image_filename).replace("\\", "/")
            return f"![{alt_text}]({relative_path})"
        else:
            encoded_string = base64.b64encode(image_bytes).decode("utf-8")
            return f"![{alt_text}](data:image/{image_format};base64,{encoded_string})"
            
    def _perform_ocr_on_image_bytes(self, image_bytes: bytes) -> str:
        """Effectue l'OCR sur des bytes d'image en utilisant Doctr."""
        try:
            self._initialize_ocr_reader()
            if not self.ocr_predictor: return ""
            
            doc = DocumentFile.from_images([image_bytes])
            
            # CORRECTION : L'appel au prédicteur se fait sans l'argument 'languages'.
            # Le modèle pré-entraîné par défaut est déjà multilingue.
            result = self.ocr_predictor(doc)
            
            return result.render().strip()

        except Exception as e:
            import traceback
            print(f"  - OCR ERROR : {e}")
            traceback.print_exc()
            return ""

    def _extract_content_from_single_file(self, input_path: str) -> str:
        """
        Extrait le contenu en utilisant la stratégie la plus adaptée au type de fichier.
        Pour les PDF, chaque page est traitée comme une image pour une robustesse maximale.
        """
        file_basename = os.path.basename(input_path)
        file_root, file_extension = os.path.splitext(file_basename)
        file_extension = file_extension.lower()
        
        if file_extension == '.pdf':
            all_pages_content = []
            with fitz.open(input_path) as doc:
                if doc.is_encrypted: return "[Content not extractable – Encrypted PDF]"

                for i, page in enumerate(doc):
                    print(f"    - Processing page {i + 1}/{len(doc)}...")
                    
                    pix = page.get_pixmap(dpi=self.image_dpi)
                    img_bytes = pix.tobytes("png")
                    
                    if self.perform_ocr:
                        ocr_text = self._perform_ocr_on_image_bytes(img_bytes)
                        if ocr_text:
                            page_content = f"## Page {i + 1}\n\n{ocr_text}"
                            all_pages_content.append(page_content)
                            print(f"      - OCR successful on the page {i + 1}.")
                        else:
                            print(f"      - OCR yielded no results for page {i + 1}, saving as image.")
                            img_filename = f"{self.output_basename}_p{i+1}_full.png"
                            md_image = self._get_image_markdown(img_bytes, f"Page {i+1} contains no detected text", "png", img_filename)
                            all_pages_content.append(f"## Page {i + 1} (Image)\n\n{md_image}")
                    else:
                        img_filename = f"{self.output_basename}_p{i+1}_full.png"
                        md_image = self._get_image_markdown(img_bytes, f"Page {i+1}", "png", img_filename)
                        all_pages_content.append(f"## Page {i + 1} (Image)\n\n{md_image}")

            return "\n\n---\n\n".join(all_pages_content)
        
        elif file_extension in self.SUPPORTED_IMAGE_EXTENSIONS:
            print(f"  Processing the image '{file_basename}'...")
            with open(input_path, "rb") as image_file:
                img_bytes = image_file.read()

            if self.perform_ocr:
                ocr_text = self._perform_ocr_on_image_bytes(img_bytes)
                if ocr_text: return ocr_text
            
            image_format = file_extension.strip('.')
            image_filename = f"{self.output_basename}_{file_root}.{image_format}"
            return self._get_image_markdown(img_bytes, file_basename, image_format, image_filename)

        else:
            return f"[ERROR: Unsupported file type : {file_extension}]"

    def _save_outputs(self, final_content: str):
        """Sauvegarde les contenus extraits dans les fichiers de sortie."""
        print(f"\n[Saving the results] ...")
        txt_content = re.sub(r"!\[.*?\]\(.*?\)", "[Image]", final_content)
        for path, content in [(self.output_md_path, final_content), (self.output_txt_path, txt_content)]:
            try:
                with open(path, 'w', encoding='utf-8') as f: f.write(content)
                print(f"  - Success: output saved to '{path}'.")
            except IOError as e: print(f"  - ERROR: Unable to write to '{path}'. Error occurred: {e}")
    
    def _print_result_to_console(self, filename: str, content: str):
        """Affiche le résultat textuel dans la console."""
        print("\n" + "="*20 + f" CONTENT OF {filename} " + "="*20)
        console_content = re.sub(r"!\[.*?\]\(.*?\)", "[Image]", content)
        print(console_content)
        print("="* (44 + len(filename)) + "\n")

    def __str__(self) -> str:
        """Retourne un résumé de l'opération d'extraction."""
        summary_lines = [f"--- Summary of RostaingOCR extraction ---"]
        if not self.results: return "\n".join(summary_lines + ["No files were processed."])
        
        summary_lines.append(f"Output files: '{self.output_txt_path}', '{self.output_md_path}'")
        if self.save_images_externally:
             summary_lines.append(f"Images (if OCR fails) saved in: '{self.image_output_dir}/'")
        
        ocr_status = f"Yes (Languages supported by the model): {self.ocr_lang})" if self.perform_ocr else "No"
        summary_lines.append(f"OCR enabled: {ocr_status}")
        
        for file_path, content in self.results.items():
            status = "✅ Success" if content and not content.startswith("[ERROR") else "❌ Failure"
            summary_lines.append(f"\n  - File processed : {os.path.basename(file_path)}")
            summary_lines.append(f"    Status         : {status}")
            
        return "\n".join(summary_lines)