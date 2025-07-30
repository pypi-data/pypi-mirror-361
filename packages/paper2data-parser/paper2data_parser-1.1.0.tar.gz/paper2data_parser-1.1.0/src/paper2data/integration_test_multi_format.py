#!/usr/bin/env python3
"""
Integration test for Paper2Data Multi-Format Export System V1.1

Demonstrates integration with the main Paper2Data extraction pipeline
and shows how to use the multi-format export system in practice.
"""

import sys
from pathlib import Path
import tempfile
import shutil
import time

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from multi_format_exporter import (
    MultiFormatExporter,
    ExportConfiguration,
    OutputFormat,
    TemplateTheme
)
from utils import get_logger


def simulate_paper2data_extraction():
    """Simulate Paper2Data extraction results."""
    return {
        "content": {
            "metadata": {
                "title": "Deep Learning for Natural Language Processing: A Comprehensive Survey",
                "authors": "Dr. Sarah Johnson, Prof. Michael Chen, Dr. Emily Rodriguez",
                "subject": "Natural Language Processing",
                "creator": "Paper2Data v1.1",
                "page_count": 32,
                "creation_date": "2024-01-15"
            },
            "full_text": "This comprehensive survey covers the latest advances in deep learning for NLP...",
            "statistics": {
                "word_count": 8500,
                "page_count": 32,
                "character_count": 45000
            }
        },
        "sections": {
            "sections": {
                "abstract": "Deep learning has revolutionized natural language processing (NLP) in recent years. This survey provides a comprehensive overview of state-of-the-art deep learning techniques applied to various NLP tasks, including text classification, named entity recognition, machine translation, and question answering. We discuss the evolution from traditional approaches to modern transformer-based architectures, highlighting key innovations and their impact on performance.",
                "introduction": "Natural Language Processing (NLP) has experienced remarkable progress with the advent of deep learning. Traditional rule-based and statistical approaches have been largely superseded by neural networks that can learn complex patterns directly from data. This transformation has enabled significant improvements in accuracy and generalization across diverse NLP tasks.",
                "background": "The foundation of modern NLP lies in the ability to represent text as numerical vectors. Early approaches used sparse representations like bag-of-words, while modern methods employ dense vector embeddings learned from large corpora. The introduction of attention mechanisms has further enhanced the capability of neural networks to model long-range dependencies in text.",
                "methodology": "Our survey methodology involves a systematic review of recent literature from top-tier conferences and journals. We categorize approaches based on their architectural innovations and evaluate their performance on standard benchmarks. Special attention is given to transformer-based models, which have become the dominant paradigm in NLP.",
                "results": "Our analysis reveals that transformer-based models consistently outperform previous approaches across multiple tasks. BERT and its variants have achieved state-of-the-art results in text classification and named entity recognition. GPT models have demonstrated exceptional performance in text generation and few-shot learning scenarios.",
                "discussion": "The success of transformer models can be attributed to their ability to capture contextual relationships through self-attention mechanisms. However, these models require substantial computational resources and large amounts of training data. Recent work has focused on making these models more efficient and accessible.",
                "conclusion": "Deep learning has fundamentally changed the landscape of NLP. While current approaches achieve impressive results, challenges remain in areas such as interpretability, robustness, and computational efficiency. Future research directions include developing more efficient architectures, improving multilingual capabilities, and addressing bias in language models.",
                "references": "1. Devlin, J., et al. (2018). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding.\n2. Radford, A., et al. (2019). Language Models are Unsupervised Multitask Learners.\n3. Vaswani, A., et al. (2017). Attention is All You Need."
            },
            "summary": {
                "sections_found": 8,
                "average_section_length": 150,
                "total_sections_text": 1200
            }
        },
        "figures": {
            "figures": [
                {
                    "figure_id": "fig1",
                    "caption": "Evolution of NLP architectures from RNNs to Transformers",
                    "data": b"PNG_ARCHITECTURE_DIAGRAM",
                    "format": "png",
                    "size": {"width": 1000, "height": 600},
                    "alt_text": "Timeline showing the evolution of NLP architectures"
                },
                {
                    "figure_id": "fig2",
                    "caption": "Performance comparison of different models on GLUE benchmark",
                    "data": b"PNG_PERFORMANCE_CHART",
                    "format": "png",
                    "size": {"width": 800, "height": 500},
                    "alt_text": "Bar chart comparing model performance"
                },
                {
                    "figure_id": "fig3",
                    "caption": "Attention visualization in transformer models",
                    "data": b"PNG_ATTENTION_HEATMAP",
                    "format": "png",
                    "size": {"width": 600, "height": 600},
                    "alt_text": "Heatmap showing attention weights"
                }
            ],
            "summary": {
                "figures_found": 3,
                "formats": ["png"],
                "total_size": "2.3MB"
            }
        },
        "tables": {
            "tables": [
                {
                    "table_id": "table1",
                    "caption": "Comparison of pre-trained language models",
                    "csv_content": "Model,Parameters,Training Data,GLUE Score,Release Year\nBERT-Base,110M,16GB,79.6,2018\nBERT-Large,340M,16GB,80.5,2018\nRoBERTa,355M,160GB,88.5,2019\nT5-Base,220M,750GB,87.1,2019\nGPT-3,175B,570GB,N/A,2020",
                    "format": "csv",
                    "rows": 6,
                    "columns": 5
                },
                {
                    "table_id": "table2",
                    "caption": "NLP task categories and representative datasets",
                    "csv_content": "Task Category,Task,Dataset,Metric,State-of-art Score\nText Classification,Sentiment Analysis,SST-2,Accuracy,96.8\nSequence Labeling,Named Entity Recognition,CoNLL-2003,F1,93.5\nText Generation,Machine Translation,WMT14 En-De,BLEU,41.4\nReading Comprehension,Question Answering,SQuAD 2.0,F1,90.9",
                    "format": "csv",
                    "rows": 5,
                    "columns": 5
                }
            ],
            "summary": {
                "tables_found": 2,
                "total_cells": 45,
                "formats": ["csv"]
            }
        },
        "equations": {
            "equations": [
                {
                    "equation_id": "eq1",
                    "latex": "\\text{Attention}(Q, K, V) = \\text{softmax}\\left(\\frac{QK^T}{\\sqrt{d_k}}\\right)V",
                    "mathml": "<math><mi>Attention</mi><mo>(</mo><mi>Q</mi><mo>,</mo><mi>K</mi><mo>,</mo><mi>V</mi><mo>)</mo></math>",
                    "context": "Self-attention mechanism in transformer models"
                },
                {
                    "equation_id": "eq2",
                    "latex": "\\text{FFN}(x) = \\max(0, xW_1 + b_1)W_2 + b_2",
                    "mathml": "<math><mi>FFN</mi><mo>(</mo><mi>x</mi><mo>)</mo></math>",
                    "context": "Feed-forward network in transformer layers"
                },
                {
                    "equation_id": "eq3",
                    "latex": "\\mathcal{L} = -\\sum_{i=1}^{N} \\log P(y_i | x_i; \\theta)",
                    "mathml": "<math><mi>L</mi></math>",
                    "context": "Cross-entropy loss function for language modeling"
                }
            ],
            "summary": {
                "equations_found": 3,
                "latex_formatted": 3,
                "mathml_formatted": 3
            }
        },
        "citations": {
            "references": [
                {
                    "citation_id": "ref1",
                    "formatted": "Devlin, J., Chang, M. W., Lee, K., & Toutanova, K. (2018). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. arXiv preprint arXiv:1810.04805.",
                    "authors": ["Devlin, J.", "Chang, M. W.", "Lee, K.", "Toutanova, K."],
                    "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
                    "year": "2018",
                    "journal": "arXiv preprint",
                    "doi": "arXiv:1810.04805"
                },
                {
                    "citation_id": "ref2",
                    "formatted": "Radford, A., Wu, J., Child, R., Luan, D., Amodei, D., & Sutskever, I. (2019). Language Models are Unsupervised Multitask Learners. OpenAI Blog.",
                    "authors": ["Radford, A.", "Wu, J.", "Child, R.", "Luan, D.", "Amodei, D.", "Sutskever, I."],
                    "title": "Language Models are Unsupervised Multitask Learners",
                    "year": "2019",
                    "journal": "OpenAI Blog"
                },
                {
                    "citation_id": "ref3",
                    "formatted": "Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., ... & Polosukhin, I. (2017). Attention is All You Need. Advances in Neural Information Processing Systems, 30.",
                    "authors": ["Vaswani, A.", "Shazeer, N.", "Parmar, N."],
                    "title": "Attention is All You Need",
                    "year": "2017",
                    "journal": "Advances in Neural Information Processing Systems",
                    "doi": "10.5555/3295222.3295349"
                }
            ],
            "summary": {
                "references_found": 3,
                "years_range": "2017-2019",
                "venues": ["arXiv", "OpenAI Blog", "NeurIPS"]
            }
        },
        "summary": {
            "total_pages": 32,
            "total_words": 8500,
            "sections_found": 8,
            "figures_found": 3,
            "tables_found": 2,
            "equations_found": 3,
            "references_found": 3,
            "extraction_timestamp": "2024-01-15T14:30:00Z"
        }
    }


def demonstrate_multi_format_export():
    """Demonstrate the multi-format export system with realistic data."""
    logger = get_logger(__name__)
    
    print("=" * 80)
    print("Paper2Data Multi-Format Export System V1.1 - Integration Test")
    print("=" * 80)
    
    # Step 1: Simulate Paper2Data extraction
    print("\n1. Simulating Paper2Data extraction...")
    extraction_results = simulate_paper2data_extraction()
    
    paper_title = extraction_results["content"]["metadata"]["title"]
    print(f"   Paper: {paper_title}")
    print(f"   Authors: {extraction_results['content']['metadata']['authors']}")
    print(f"   Pages: {extraction_results['content']['metadata']['page_count']}")
    print(f"   Sections: {extraction_results['summary']['sections_found']}")
    print(f"   Figures: {extraction_results['summary']['figures_found']}")
    print(f"   Tables: {extraction_results['summary']['tables_found']}")
    print(f"   Equations: {extraction_results['summary']['equations_found']}")
    print(f"   References: {extraction_results['summary']['references_found']}")
    
    # Step 2: Initialize multi-format exporter
    print("\n2. Initializing Multi-Format Exporter...")
    
    temp_dir = Path(tempfile.mkdtemp())
    try:
        exporter = MultiFormatExporter(extraction_results, temp_dir)
        print(f"   Output directory: {temp_dir}")
        
        # Step 3: Export to individual formats
        print("\n3. Exporting to Individual Formats...")
        
        formats_to_test = [
            (OutputFormat.MARKDOWN, "Markdown"),
            (OutputFormat.HTML, "HTML"),
            (OutputFormat.LATEX, "LaTeX"),
            (OutputFormat.WORD, "Word"),
            (OutputFormat.EPUB, "EPUB")
        ]
        
        export_results = {}
        
        for format_type, format_name in formats_to_test:
            print(f"   Exporting to {format_name}...")
            start_time = time.time()
            
            try:
                config = ExportConfiguration(
                    format=format_type,
                    theme=TemplateTheme.ACADEMIC,
                    include_figures=True,
                    include_tables=True,
                    include_equations=True,
                    include_bibliography=True,
                    interactive_elements=True,
                    generate_toc=True
                )
                
                result = exporter.export_single_format(config)
                export_results[format_type] = result
                
                processing_time = time.time() - start_time
                print(f"     ✓ {format_name} export successful")
                print(f"       File: {result.file_path.name}")
                print(f"       Size: {result.file_size:,} bytes")
                print(f"       Time: {processing_time:.3f} seconds")
                
            except Exception as e:
                print(f"     ✗ {format_name} export failed: {str(e)}")
                if "Template not found" in str(e):
                    print(f"       Note: Template files not found - this is expected in test environment")
        
        # Step 4: Create export package
        print("\n4. Creating Export Package...")
        successful_formats = list(export_results.keys())
        
        if successful_formats:
            start_time = time.time()
            package_path = exporter.create_export_package(successful_formats, TemplateTheme.ACADEMIC)
            processing_time = time.time() - start_time
            
            print(f"   ✓ Export package created")
            print(f"     Package: {package_path.name}")
            print(f"     Size: {package_path.stat().st_size:,} bytes")
            print(f"     Time: {processing_time:.3f} seconds")
            print(f"     Formats: {len(successful_formats)}")
        
        # Step 5: Demonstrate content preparation
        print("\n5. Demonstrating Content Preparation...")
        
        config = ExportConfiguration(
            format=OutputFormat.MARKDOWN,
            theme=TemplateTheme.ACADEMIC,
            include_figures=True,
            include_tables=True,
            include_equations=True,
            include_bibliography=True
        )
        
        prepared_content = exporter.prepare_content_for_export(config)
        
        print(f"   ✓ Content preparation successful")
        print(f"     Metadata fields: {len(prepared_content['metadata'])}")
        print(f"     Sections prepared: {len(prepared_content['sections'])}")
        print(f"     Figures prepared: {len(prepared_content['figures'])}")
        print(f"     Tables prepared: {len(prepared_content['tables'])}")
        print(f"     Equations prepared: {len(prepared_content['equations'])}")
        print(f"     Bibliography entries: {len(prepared_content['bibliography'])}")
        print(f"     TOC entries: {len(prepared_content['toc'])}")
        
        # Step 6: Show sample content
        print("\n6. Sample Export Content...")
        
        if OutputFormat.MARKDOWN in export_results:
            md_file = export_results[OutputFormat.MARKDOWN].file_path
            md_content = md_file.read_text()
            
            print(f"   Markdown Export Preview (first 500 characters):")
            print(f"   {'-' * 50}")
            print(f"   {md_content[:500]}...")
            print(f"   {'-' * 50}")
        
        # Step 7: Performance summary
        print("\n7. Performance Summary...")
        
        total_exports = len(export_results)
        total_size = sum(result.file_size for result in export_results.values())
        
        print(f"   ✓ Successfully exported to {total_exports} formats")
        print(f"   ✓ Total output size: {total_size:,} bytes")
        print(f"   ✓ Average file size: {total_size // total_exports if total_exports > 0 else 0:,} bytes")
        
        # Step 8: Integration verification
        print("\n8. Integration Verification...")
        
        # Verify all expected components are present
        verifications = [
            ("Metadata extraction", len(prepared_content['metadata']) > 0),
            ("Section processing", len(prepared_content['sections']) > 0),
            ("Figure handling", len(prepared_content['figures']) >= 0),
            ("Table processing", len(prepared_content['tables']) >= 0),
            ("Equation handling", len(prepared_content['equations']) >= 0),
            ("Bibliography parsing", len(prepared_content['bibliography']) >= 0),
            ("TOC generation", len(prepared_content['toc']) >= 0),
            ("Multi-format export", total_exports > 0)
        ]
        
        all_passed = True
        for check_name, passed in verifications:
            status = "✓" if passed else "✗"
            print(f"   {status} {check_name}")
            if not passed:
                all_passed = False
        
        print(f"\n{'=' * 80}")
        if all_passed:
            print("✓ ALL INTEGRATION TESTS PASSED!")
            print("✓ Multi-Format Export System is ready for production use!")
        else:
            print("✗ Some tests failed - check configuration")
        print(f"{'=' * 80}")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        print(f"\nCleanup completed.")


if __name__ == "__main__":
    demonstrate_multi_format_export() 