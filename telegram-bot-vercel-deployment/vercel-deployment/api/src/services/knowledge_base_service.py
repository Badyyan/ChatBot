import re
from src.models.bot import db, Bot, KnowledgeBase, Document, TextChunk
from sqlalchemy import or_, and_

class KnowledgeBaseService:
    def __init__(self):
        self.max_results = 5
        self.min_score_threshold = 0.1
    
    def search_knowledge_base(self, bot_id: int, query: str, max_results: int = None):
        """Search the knowledge base for relevant information"""
        if max_results is None:
            max_results = self.max_results
        
        # Get all knowledge bases for the bot
        knowledge_bases = KnowledgeBase.query.filter_by(bot_id=bot_id).all()
        if not knowledge_bases:
            return None
        
        kb_ids = [kb.id for kb in knowledge_bases]
        
        # Search for relevant text chunks
        relevant_chunks = self._search_chunks(kb_ids, query, max_results)
        
        if not relevant_chunks:
            return None
        
        # Format the response
        response = self._format_response(relevant_chunks, query)
        return response
    
    def _search_chunks(self, kb_ids: list, query: str, max_results: int):
        """Search for relevant text chunks using simple text matching"""
        # Clean and prepare query
        query_words = self._extract_keywords(query.lower())
        
        if not query_words:
            return []
        
        # Get all documents from the knowledge bases
        documents = Document.query.filter(
            Document.knowledge_base_id.in_(kb_ids),
            Document.processed == True
        ).all()
        
        if not documents:
            return []
        
        doc_ids = [doc.id for doc in documents]
        
        # Get all text chunks from these documents
        chunks = TextChunk.query.filter(
            TextChunk.document_id.in_(doc_ids)
        ).all()
        
        # Score chunks based on keyword matching
        scored_chunks = []
        for chunk in chunks:
            score = self._calculate_relevance_score(chunk.content.lower(), query_words)
            if score > self.min_score_threshold:
                scored_chunks.append((chunk, score))
        
        # Sort by score and return top results
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, score in scored_chunks[:max_results]]
    
    def _extract_keywords(self, text: str):
        """Extract meaningful keywords from text"""
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
            'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their', 'what',
            'when', 'where', 'why', 'how', 'who', 'which'
        }
        
        # Extract words (alphanumeric sequences)
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out stop words and short words
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        return keywords
    
    def _calculate_relevance_score(self, content: str, query_words: list):
        """Calculate relevance score based on keyword matching"""
        if not query_words:
            return 0
        
        content_words = self._extract_keywords(content)
        content_text = ' '.join(content_words)
        
        score = 0
        total_words = len(query_words)
        
        for word in query_words:
            # Exact word match
            if word in content_words:
                score += 1.0
            # Partial match (word contains query word or vice versa)
            elif any(word in content_word or content_word in word for content_word in content_words if len(word) > 3):
                score += 0.5
        
        # Normalize score
        return score / total_words if total_words > 0 else 0
    
    def _format_response(self, chunks: list, query: str):
        """Format the response from relevant chunks"""
        if not chunks:
            return None
        
        # Combine relevant information
        response_parts = []
        
        response_parts.append("Based on the information in my knowledge base:\n")
        
        # Add relevant content from chunks
        for i, chunk in enumerate(chunks[:3], 1):  # Limit to top 3 chunks
            # Get document info
            document = Document.query.get(chunk.document_id)
            
            # Clean and truncate content
            content = chunk.content.strip()
            if len(content) > 300:
                content = content[:300] + "..."
            
            response_parts.append(f"📄 From {document.original_filename}:")
            response_parts.append(content)
            response_parts.append("")  # Empty line for spacing
        
        # Add footer
        if len(chunks) > 3:
            response_parts.append(f"💡 Found {len(chunks)} relevant sections. Showing top 3.")
        
        return "\n".join(response_parts)
    
    def get_knowledge_base_stats(self, bot_id: int):
        """Get statistics about the knowledge base"""
        knowledge_bases = KnowledgeBase.query.filter_by(bot_id=bot_id).all()
        
        total_documents = 0
        total_chunks = 0
        processed_documents = 0
        
        for kb in knowledge_bases:
            documents = Document.query.filter_by(knowledge_base_id=kb.id).all()
            total_documents += len(documents)
            processed_documents += len([doc for doc in documents if doc.processed])
            
            for doc in documents:
                total_chunks += len(doc.chunks)
        
        return {
            'knowledge_bases': len(knowledge_bases),
            'total_documents': total_documents,
            'processed_documents': processed_documents,
            'total_chunks': total_chunks,
            'processing_complete': processed_documents == total_documents
        }
    
    def search_documents(self, kb_id: int, query: str):
        """Search for documents by name or content"""
        kb = KnowledgeBase.query.get(kb_id)
        if not kb:
            return []
        
        query_lower = query.lower()
        
        # Search by filename
        documents = Document.query.filter(
            Document.knowledge_base_id == kb_id,
            or_(
                Document.original_filename.ilike(f'%{query}%'),
                Document.filename.ilike(f'%{query}%')
            )
        ).all()
        
        return documents

