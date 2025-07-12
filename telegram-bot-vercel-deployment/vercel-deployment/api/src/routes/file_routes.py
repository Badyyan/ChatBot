from flask import Blueprint, request, jsonify, current_app
from src.models.bot import db, KnowledgeBase, Document
from src.services.file_processor import FileProcessor
import threading
import os

file_bp = Blueprint('file', __name__)

def get_file_processor():
    """Get file processor instance"""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return FileProcessor(upload_folder)

@file_bp.route('/knowledge-bases/<int:kb_id>/upload', methods=['POST'])
def upload_file(kb_id):
    """Upload a file to a knowledge base"""
    try:
        # Check if knowledge base exists
        kb = KnowledgeBase.query.get_or_404(kb_id)
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        processor = get_file_processor()
        
        # Save file
        document = processor.save_file(file, kb_id)
        
        # Process file in background
        def process_file():
            try:
                processor.process_document(document.id)
            except Exception as e:
                print(f"Error processing document {document.id}: {e}")
        
        thread = threading.Thread(target=process_file, daemon=True)
        thread.start()
        
        return jsonify({
            'success': True,
            'data': document.to_dict(),
            'message': 'File uploaded successfully. Processing in background.'
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@file_bp.route('/knowledge-bases/<int:kb_id>/documents', methods=['GET'])
def get_documents(kb_id):
    """Get all documents in a knowledge base"""
    try:
        kb = KnowledgeBase.query.get_or_404(kb_id)
        
        documents = Document.query.filter_by(knowledge_base_id=kb_id)\
            .order_by(Document.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [doc.to_dict() for doc in documents]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@file_bp.route('/documents/<int:doc_id>', methods=['GET'])
def get_document(doc_id):
    """Get detailed information about a document"""
    try:
        processor = get_file_processor()
        doc_info = processor.get_document_info(doc_id)
        
        if not doc_info:
            return jsonify({
                'success': False,
                'error': 'Document not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': doc_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@file_bp.route('/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """Delete a document"""
    try:
        processor = get_file_processor()
        success = processor.delete_document(doc_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Document deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Document not found'
            }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@file_bp.route('/documents/<int:doc_id>/process', methods=['POST'])
def process_document(doc_id):
    """Manually trigger document processing"""
    try:
        processor = get_file_processor()
        
        # Process in background
        def process_file():
            try:
                processor.process_document(doc_id)
            except Exception as e:
                print(f"Error processing document {doc_id}: {e}")
        
        thread = threading.Thread(target=process_file, daemon=True)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Document processing started'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@file_bp.route('/documents/<int:doc_id>/chunks', methods=['GET'])
def get_document_chunks(doc_id):
    """Get text chunks for a document"""
    try:
        document = Document.query.get_or_404(doc_id)
        
        chunks = []
        for chunk in document.chunks:
            chunks.append(chunk.to_dict())
        
        return jsonify({
            'success': True,
            'data': chunks
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@file_bp.route('/knowledge-bases/<int:kb_id>/search', methods=['POST'])
def search_knowledge_base(kb_id):
    """Search within a specific knowledge base"""
    try:
        kb = KnowledgeBase.query.get_or_404(kb_id)
        data = request.get_json()
        
        if not data or not data.get('query'):
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        query = data['query']
        max_results = data.get('max_results', 5)
        
        from src.services.knowledge_base_service import KnowledgeBaseService
        kb_service = KnowledgeBaseService()
        
        # Search in this specific knowledge base
        relevant_chunks = kb_service._search_chunks([kb_id], query, max_results)
        
        results = []
        for chunk in relevant_chunks:
            document = Document.query.get(chunk.document_id)
            results.append({
                'chunk': chunk.to_dict(),
                'document': {
                    'id': document.id,
                    'filename': document.original_filename,
                    'file_type': document.file_type
                }
            })
        
        return jsonify({
            'success': True,
            'data': results,
            'query': query
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@file_bp.route('/knowledge-bases/<int:kb_id>/stats', methods=['GET'])
def get_knowledge_base_stats(kb_id):
    """Get statistics for a knowledge base"""
    try:
        kb = KnowledgeBase.query.get_or_404(kb_id)
        
        from src.services.knowledge_base_service import KnowledgeBaseService
        kb_service = KnowledgeBaseService()
        
        # Get stats for the bot (will include this KB)
        stats = kb_service.get_knowledge_base_stats(kb.bot_id)
        
        # Get specific stats for this KB
        documents = Document.query.filter_by(knowledge_base_id=kb_id).all()
        processed_docs = [doc for doc in documents if doc.processed]
        
        total_chunks = 0
        for doc in documents:
            total_chunks += len(doc.chunks)
        
        kb_stats = {
            'knowledge_base_id': kb_id,
            'name': kb.name,
            'documents': len(documents),
            'processed_documents': len(processed_docs),
            'total_chunks': total_chunks,
            'processing_complete': len(processed_docs) == len(documents)
        }
        
        return jsonify({
            'success': True,
            'data': kb_stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

