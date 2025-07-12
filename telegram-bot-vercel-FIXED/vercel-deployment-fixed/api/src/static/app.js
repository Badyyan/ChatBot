// Telegram Bot Dashboard JavaScript

// Global variables
let currentBot = null;
let currentKnowledgeBase = null;
let bots = [];
let knowledgeBases = [];

// API Base URL
const API_BASE = '/api';

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadDashboard();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Bot selection change
    document.getElementById('kb-bot-select').addEventListener('change', function() {
        const botId = this.value;
        if (botId) {
            currentBot = parseInt(botId);
            loadKnowledgeBases(botId);
            document.getElementById('upload-btn').disabled = false;
        } else {
            currentBot = null;
            document.getElementById('knowledge-bases-list').innerHTML = '<p class="text-muted">Select a bot to view knowledge bases</p>';
            document.getElementById('documents-list').innerHTML = '<p class="text-muted">Select a knowledge base to view documents</p>';
            document.getElementById('upload-btn').disabled = true;
        }
    });
}

// Show/hide sections
function showSection(sectionName) {
    // Hide all sections
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {
        section.style.display = 'none';
    });
    
    // Show selected section
    document.getElementById(sectionName + '-section').style.display = 'block';
    
    // Update navigation
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.classList.remove('active');
    });
    
    // Find and activate the correct nav link
    const activeLink = document.querySelector(`[onclick="showSection('${sectionName}')"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
    
    // Load section-specific data
    switch(sectionName) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'bots':
            loadBots();
            break;
        case 'knowledge':
            loadKnowledgeSection();
            break;
        case 'analytics':
            loadAnalytics();
            break;
    }
}

// Load dashboard data
async function loadDashboard() {
    try {
        showLoading(true);
        
        // Load stats
        await loadStats();
        
        // Load recent activity
        await loadRecentActivity();
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showNotification('Error loading dashboard data', 'error');
    } finally {
        showLoading(false);
    }
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/bots`);
        const data = await response.json();
        
        if (data.success) {
            bots = data.data;
            const totalBots = bots.length;
            const activeBots = bots.filter(bot => bot.is_active).length;
            
            document.getElementById('total-bots').textContent = totalBots;
            document.getElementById('active-bots').textContent = activeBots;
            
            // Calculate total knowledge bases and documents
            let totalKB = 0;
            let totalDocs = 0;
            
            for (const bot of bots) {
                totalKB += bot.knowledge_bases_count || 0;
                
                // Get documents count for each bot
                try {
                    const kbResponse = await fetch(`${API_BASE}/bots/${bot.id}/knowledge-bases`);
                    const kbData = await kbResponse.json();
                    if (kbData.success) {
                        for (const kb of kbData.data) {
                            totalDocs += kb.documents_count || 0;
                        }
                    }
                } catch (error) {
                    console.error('Error loading KB data for bot', bot.id, error);
                }
            }
            
            document.getElementById('total-kb').textContent = totalKB;
            document.getElementById('total-docs').textContent = totalDocs;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load recent activity
async function loadRecentActivity() {
    const activityContainer = document.getElementById('recent-activity');
    
    try {
        // For now, show sample activity
        const activities = [
            { type: 'success', message: 'Bot "Customer Support" started successfully', time: '2 minutes ago' },
            { type: 'info', message: 'New document uploaded to Knowledge Base', time: '15 minutes ago' },
            { type: 'warning', message: 'Bot "FAQ Bot" stopped responding', time: '1 hour ago' },
            { type: 'success', message: 'Knowledge Base processed 5 new documents', time: '2 hours ago' }
        ];
        
        let html = '';
        activities.forEach(activity => {
            html += `
                <div class="activity-item ${activity.type}">
                    <div class="d-flex justify-content-between">
                        <span>${activity.message}</span>
                        <small class="text-muted">${activity.time}</small>
                    </div>
                </div>
            `;
        });
        
        activityContainer.innerHTML = html;
    } catch (error) {
        activityContainer.innerHTML = '<p class="text-muted">Error loading activity</p>';
    }
}

// Load bots
async function loadBots() {
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/bots`);
        const data = await response.json();
        
        if (data.success) {
            bots = data.data;
            displayBots(bots);
            
            // Also load bot statuses
            await loadBotStatuses();
        } else {
            showNotification('Error loading bots: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error loading bots:', error);
        showNotification('Error loading bots', 'error');
    } finally {
        showLoading(false);
    }
}

// Load bot statuses
async function loadBotStatuses() {
    try {
        const response = await fetch(`${API_BASE}/bots/status`);
        const data = await response.json();
        
        if (data.success) {
            // Update bot display with status
            data.data.forEach(botStatus => {
                const botCard = document.querySelector(`[data-bot-id="${botStatus.bot_id}"]`);
                if (botCard) {
                    const statusBadge = botCard.querySelector('.bot-status');
                    const startBtn = botCard.querySelector('.start-btn');
                    const stopBtn = botCard.querySelector('.stop-btn');
                    
                    if (botStatus.is_running) {
                        statusBadge.className = 'bot-status running';
                        statusBadge.innerHTML = '<i class="fas fa-circle"></i> Running';
                        startBtn.style.display = 'none';
                        stopBtn.style.display = 'inline-block';
                        botCard.classList.add('running');
                        botCard.classList.remove('stopped');
                    } else {
                        statusBadge.className = 'bot-status stopped';
                        statusBadge.innerHTML = '<i class="fas fa-circle"></i> Stopped';
                        startBtn.style.display = 'inline-block';
                        stopBtn.style.display = 'none';
                        botCard.classList.add('stopped');
                        botCard.classList.remove('running');
                    }
                }
            });
        }
    } catch (error) {
        console.error('Error loading bot statuses:', error);
    }
}

// Display bots
function displayBots(bots) {
    const container = document.getElementById('bots-list');
    
    if (bots.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-robot fa-3x text-muted mb-3"></i>
                <h5>No bots created yet</h5>
                <p class="text-muted">Create your first bot to get started</p>
                <button class="btn btn-primary" onclick="showCreateBotModal()">
                    <i class="fas fa-plus me-2"></i>Create New Bot
                </button>
            </div>
        `;
        return;
    }
    
    let html = '<div class="row">';
    
    bots.forEach(bot => {
        html += `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card bot-card" data-bot-id="${bot.id}">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <h5 class="card-title mb-0">${bot.name}</h5>
                            <span class="bot-status">
                                <i class="fas fa-circle"></i> Loading...
                            </span>
                        </div>
                        <p class="text-muted mb-2">@${bot.username}</p>
                        <p class="card-text">${bot.description || 'No description'}</p>
                        <div class="d-flex gap-2">
                            <button class="btn btn-success btn-sm start-btn" onclick="startBot(${bot.id})">
                                <i class="fas fa-play me-1"></i>Start
                            </button>
                            <button class="btn btn-danger btn-sm stop-btn" onclick="stopBot(${bot.id})" style="display: none;">
                                <i class="fas fa-stop me-1"></i>Stop
                            </button>
                            <button class="btn btn-outline-primary btn-sm" onclick="editBot(${bot.id})">
                                <i class="fas fa-edit me-1"></i>Edit
                            </button>
                            <button class="btn btn-outline-danger btn-sm" onclick="deleteBot(${bot.id})">
                                <i class="fas fa-trash me-1"></i>Delete
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

// Load knowledge section
async function loadKnowledgeSection() {
    try {
        // Load bots for selection
        const response = await fetch(`${API_BASE}/bots`);
        const data = await response.json();
        
        if (data.success) {
            const select = document.getElementById('kb-bot-select');
            select.innerHTML = '<option value="">Select a bot...</option>';
            
            data.data.forEach(bot => {
                select.innerHTML += `<option value="${bot.id}">${bot.name} (@${bot.username})</option>`;
            });
        }
    } catch (error) {
        console.error('Error loading knowledge section:', error);
    }
}

// Load knowledge bases for a bot
async function loadKnowledgeBases(botId) {
    try {
        const response = await fetch(`${API_BASE}/bots/${botId}/knowledge-bases`);
        const data = await response.json();
        
        if (data.success) {
            knowledgeBases = data.data;
            displayKnowledgeBases(data.data);
        } else {
            document.getElementById('knowledge-bases-list').innerHTML = '<p class="text-muted">Error loading knowledge bases</p>';
        }
    } catch (error) {
        console.error('Error loading knowledge bases:', error);
        document.getElementById('knowledge-bases-list').innerHTML = '<p class="text-muted">Error loading knowledge bases</p>';
    }
}

// Display knowledge bases
function displayKnowledgeBases(kbs) {
    const container = document.getElementById('knowledge-bases-list');
    
    if (kbs.length === 0) {
        container.innerHTML = `
            <div class="text-center py-3">
                <p class="text-muted">No knowledge bases found</p>
                <button class="btn btn-primary btn-sm" onclick="createKnowledgeBase()">
                    <i class="fas fa-plus me-1"></i>Create KB
                </button>
            </div>
        `;
        return;
    }
    
    let html = '';
    kbs.forEach(kb => {
        html += `
            <div class="card mb-2 kb-card" data-kb-id="${kb.id}" onclick="selectKnowledgeBase(${kb.id})">
                <div class="card-body p-3">
                    <h6 class="mb-1">${kb.name}</h6>
                    <small class="text-muted">${kb.documents_count || 0} documents</small>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// Select knowledge base
async function selectKnowledgeBase(kbId) {
    currentKnowledgeBase = kbId;
    
    // Update UI
    document.querySelectorAll('.kb-card').forEach(card => {
        card.classList.remove('border-primary');
    });
    document.querySelector(`[data-kb-id="${kbId}"]`).classList.add('border-primary');
    
    // Load documents
    await loadDocuments(kbId);
}

// Load documents for a knowledge base
async function loadDocuments(kbId) {
    try {
        const response = await fetch(`${API_BASE}/knowledge-bases/${kbId}/documents`);
        const data = await response.json();
        
        if (data.success) {
            displayDocuments(data.data);
        } else {
            document.getElementById('documents-list').innerHTML = '<p class="text-muted">Error loading documents</p>';
        }
    } catch (error) {
        console.error('Error loading documents:', error);
        document.getElementById('documents-list').innerHTML = '<p class="text-muted">Error loading documents</p>';
    }
}

// Display documents
function displayDocuments(documents) {
    const container = document.getElementById('documents-list');
    
    if (documents.length === 0) {
        container.innerHTML = '<p class="text-muted">No documents uploaded yet</p>';
        return;
    }
    
    let html = '';
    documents.forEach(doc => {
        const icon = getFileIcon(doc.file_type);
        const size = formatFileSize(doc.file_size);
        const status = doc.processed ? 'Processed' : 'Processing...';
        const statusClass = doc.processed ? 'success' : 'warning';
        
        html += `
            <div class="document-card">
                <div class="d-flex align-items-center">
                    <div class="document-icon ${doc.file_type}">
                        <i class="${icon}"></i>
                    </div>
                    <div class="flex-grow-1 ms-3">
                        <h6 class="mb-1">${doc.original_filename}</h6>
                        <div class="d-flex justify-content-between">
                            <small class="text-muted">${size}</small>
                            <span class="badge bg-${statusClass}">${status}</span>
                        </div>
                    </div>
                    <div class="ms-3">
                        <button class="btn btn-outline-danger btn-sm" onclick="deleteDocument(${doc.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// Bot management functions
async function startBot(botId) {
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/bots/${botId}/start`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            showNotification('Bot started successfully', 'success');
            await loadBotStatuses();
        } else {
            showNotification('Error starting bot: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error starting bot:', error);
        showNotification('Error starting bot', 'error');
    } finally {
        showLoading(false);
    }
}

async function stopBot(botId) {
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/bots/${botId}/stop`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            showNotification('Bot stopped successfully', 'success');
            await loadBotStatuses();
        } else {
            showNotification('Error stopping bot: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error stopping bot:', error);
        showNotification('Error stopping bot', 'error');
    } finally {
        showLoading(false);
    }
}

// Modal functions
function showCreateBotModal() {
    const modal = new bootstrap.Modal(document.getElementById('createBotModal'));
    modal.show();
}

function showUploadModal() {
    if (!currentBot) {
        showNotification('Please select a bot first', 'warning');
        return;
    }
    
    // Populate knowledge base select
    const select = document.getElementById('kbSelect');
    select.innerHTML = '<option value="">Select knowledge base...</option>';
    
    knowledgeBases.forEach(kb => {
        select.innerHTML += `<option value="${kb.id}">${kb.name}</option>`;
    });
    
    const modal = new bootstrap.Modal(document.getElementById('uploadModal'));
    modal.show();
}

// Create bot
async function createBot() {
    const form = document.getElementById('createBotForm');
    const formData = new FormData(form);
    
    const botData = {
        name: document.getElementById('botName').value,
        username: document.getElementById('botUsername').value,
        token: document.getElementById('botToken').value,
        description: document.getElementById('botDescription').value
    };
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/bots`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(botData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Bot created successfully', 'success');
            bootstrap.Modal.getInstance(document.getElementById('createBotModal')).hide();
            form.reset();
            await loadBots();
        } else {
            showNotification('Error creating bot: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error creating bot:', error);
        showNotification('Error creating bot', 'error');
    } finally {
        showLoading(false);
    }
}

// Upload files
async function uploadFiles() {
    const kbId = document.getElementById('kbSelect').value;
    const fileInput = document.getElementById('fileInput');
    
    if (!kbId) {
        showNotification('Please select a knowledge base', 'warning');
        return;
    }
    
    if (!fileInput.files.length) {
        showNotification('Please select files to upload', 'warning');
        return;
    }
    
    try {
        showLoading(true);
        
        for (const file of fileInput.files) {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch(`${API_BASE}/knowledge-bases/${kbId}/upload`, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (!data.success) {
                showNotification(`Error uploading ${file.name}: ${data.error}`, 'error');
            }
        }
        
        showNotification('Files uploaded successfully', 'success');
        bootstrap.Modal.getInstance(document.getElementById('uploadModal')).hide();
        document.getElementById('uploadForm').reset();
        
        // Refresh documents if we're viewing the same KB
        if (currentKnowledgeBase == kbId) {
            await loadDocuments(kbId);
        }
        
    } catch (error) {
        console.error('Error uploading files:', error);
        showNotification('Error uploading files', 'error');
    } finally {
        showLoading(false);
    }
}

// Utility functions
function getFileIcon(fileType) {
    switch (fileType.toLowerCase()) {
        case 'pdf': return 'fas fa-file-pdf';
        case 'txt': return 'fas fa-file-alt';
        case 'docx': return 'fas fa-file-word';
        case 'md': return 'fas fa-file-code';
        default: return 'fas fa-file';
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    overlay.style.display = show ? 'flex' : 'none';
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 10000; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function refreshDashboard() {
    loadDashboard();
    showNotification('Dashboard refreshed', 'success');
}

// Load analytics (placeholder)
function loadAnalytics() {
    document.getElementById('usage-stats').innerHTML = '<p class="text-muted">Analytics feature coming soon...</p>';
    document.getElementById('recent-conversations').innerHTML = '<p class="text-muted">Conversation logs coming soon...</p>';
}



// Additional bot management functions

// Create knowledge base
async function createKnowledgeBase() {
    if (!currentBot) {
        showNotification('Please select a bot first', 'warning');
        return;
    }
    
    const name = prompt('Enter knowledge base name:');
    if (!name) return;
    
    const description = prompt('Enter description (optional):') || '';
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/bots/${currentBot}/knowledge-bases`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, description })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Knowledge base created successfully', 'success');
            await loadKnowledgeBases(currentBot);
        } else {
            showNotification('Error creating knowledge base: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error creating knowledge base:', error);
        showNotification('Error creating knowledge base', 'error');
    } finally {
        showLoading(false);
    }
}

// Edit bot
async function editBot(botId) {
    const bot = bots.find(b => b.id === botId);
    if (!bot) return;
    
    const name = prompt('Enter bot name:', bot.name);
    if (!name) return;
    
    const description = prompt('Enter description:', bot.description || '');
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/bots/${botId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, description })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Bot updated successfully', 'success');
            await loadBots();
        } else {
            showNotification('Error updating bot: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error updating bot:', error);
        showNotification('Error updating bot', 'error');
    } finally {
        showLoading(false);
    }
}

// Delete bot
async function deleteBot(botId) {
    const bot = bots.find(b => b.id === botId);
    if (!bot) return;
    
    if (!confirm(`Are you sure you want to delete bot "${bot.name}"? This action cannot be undone.`)) {
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/bots/${botId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Bot deleted successfully', 'success');
            await loadBots();
        } else {
            showNotification('Error deleting bot: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error deleting bot:', error);
        showNotification('Error deleting bot', 'error');
    } finally {
        showLoading(false);
    }
}

// Delete document
async function deleteDocument(docId) {
    if (!confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/documents/${docId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Document deleted successfully', 'success');
            if (currentKnowledgeBase) {
                await loadDocuments(currentKnowledgeBase);
            }
        } else {
            showNotification('Error deleting document: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error deleting document:', error);
        showNotification('Error deleting document', 'error');
    } finally {
        showLoading(false);
    }
}

// Search knowledge base
async function searchKnowledgeBase() {
    if (!currentKnowledgeBase) {
        showNotification('Please select a knowledge base first', 'warning');
        return;
    }
    
    const query = prompt('Enter your search query:');
    if (!query) return;
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/knowledge-bases/${currentKnowledgeBase}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query, max_results: 5 })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displaySearchResults(data.data, query);
        } else {
            showNotification('Error searching: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error searching:', error);
        showNotification('Error searching knowledge base', 'error');
    } finally {
        showLoading(false);
    }
}

// Display search results
function displaySearchResults(results, query) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Search Results for "${query}"</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    ${results.length === 0 ? '<p class="text-muted">No results found</p>' : ''}
                    ${results.map(result => `
                        <div class="card mb-3">
                            <div class="card-body">
                                <h6 class="card-title">${result.document.filename}</h6>
                                <p class="card-text">${result.chunk.content}</p>
                                <small class="text-muted">From: ${result.document.filename}</small>
                            </div>
                        </div>
                    `).join('')}
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    // Remove modal from DOM when hidden
    modal.addEventListener('hidden.bs.modal', () => {
        modal.remove();
    });
}

// Enhanced knowledge base display with search button
function displayKnowledgeBases(kbs) {
    const container = document.getElementById('knowledge-bases-list');
    
    if (kbs.length === 0) {
        container.innerHTML = `
            <div class="text-center py-3">
                <p class="text-muted">No knowledge bases found</p>
                <button class="btn btn-primary btn-sm" onclick="createKnowledgeBase()">
                    <i class="fas fa-plus me-1"></i>Create KB
                </button>
            </div>
        `;
        return;
    }
    
    let html = '';
    kbs.forEach(kb => {
        html += `
            <div class="card mb-2 kb-card" data-kb-id="${kb.id}">
                <div class="card-body p-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <div onclick="selectKnowledgeBase(${kb.id})" style="cursor: pointer; flex-grow: 1;">
                            <h6 class="mb-1">${kb.name}</h6>
                            <small class="text-muted">${kb.documents_count || 0} documents</small>
                        </div>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary" onclick="searchKnowledgeBase()" title="Search">
                                <i class="fas fa-search"></i>
                            </button>
                            <button class="btn btn-outline-danger" onclick="deleteKnowledgeBase(${kb.id})" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// Delete knowledge base
async function deleteKnowledgeBase(kbId) {
    const kb = knowledgeBases.find(k => k.id === kbId);
    if (!kb) return;
    
    if (!confirm(`Are you sure you want to delete knowledge base "${kb.name}"? This will also delete all associated documents.`)) {
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/knowledge-bases/${kbId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Knowledge base deleted successfully', 'success');
            if (currentBot) {
                await loadKnowledgeBases(currentBot);
            }
            // Clear documents list if this was the selected KB
            if (currentKnowledgeBase === kbId) {
                currentKnowledgeBase = null;
                document.getElementById('documents-list').innerHTML = '<p class="text-muted">Select a knowledge base to view documents</p>';
            }
        } else {
            showNotification('Error deleting knowledge base: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error deleting knowledge base:', error);
        showNotification('Error deleting knowledge base', 'error');
    } finally {
        showLoading(false);
    }
}

// Enhanced document display with processing status
function displayDocuments(documents) {
    const container = document.getElementById('documents-list');
    
    if (documents.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-file-upload fa-3x text-muted mb-3"></i>
                <h6>No documents uploaded yet</h6>
                <p class="text-muted">Upload documents to build your knowledge base</p>
                <button class="btn btn-success" onclick="showUploadModal()">
                    <i class="fas fa-upload me-2"></i>Upload Documents
                </button>
            </div>
        `;
        return;
    }
    
    let html = '';
    documents.forEach(doc => {
        const icon = getFileIcon(doc.file_type);
        const size = formatFileSize(doc.file_size);
        const status = doc.processed ? 'Processed' : 'Processing...';
        const statusClass = doc.processed ? 'success' : 'warning';
        const statusIcon = doc.processed ? 'fas fa-check-circle' : 'fas fa-clock';
        
        html += `
            <div class="document-card">
                <div class="d-flex align-items-center">
                    <div class="document-icon ${doc.file_type}">
                        <i class="${icon}"></i>
                    </div>
                    <div class="flex-grow-1 ms-3">
                        <h6 class="mb-1">${doc.original_filename}</h6>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">${size} • ${doc.chunks_count || 0} chunks</small>
                            <span class="badge bg-${statusClass}">
                                <i class="${statusIcon} me-1"></i>${status}
                            </span>
                        </div>
                        <small class="text-muted">Uploaded: ${new Date(doc.created_at).toLocaleDateString()}</small>
                    </div>
                    <div class="ms-3">
                        <div class="btn-group btn-group-sm">
                            ${!doc.processed ? `
                                <button class="btn btn-outline-primary" onclick="processDocument(${doc.id})" title="Reprocess">
                                    <i class="fas fa-sync"></i>
                                </button>
                            ` : ''}
                            <button class="btn btn-outline-info" onclick="viewDocumentChunks(${doc.id})" title="View Chunks">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-outline-danger" onclick="deleteDocument(${doc.id})" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// Process document manually
async function processDocument(docId) {
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/documents/${docId}/process`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Document processing started', 'success');
            // Refresh documents after a delay
            setTimeout(() => {
                if (currentKnowledgeBase) {
                    loadDocuments(currentKnowledgeBase);
                }
            }, 2000);
        } else {
            showNotification('Error processing document: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error processing document:', error);
        showNotification('Error processing document', 'error');
    } finally {
        showLoading(false);
    }
}

// View document chunks
async function viewDocumentChunks(docId) {
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/documents/${docId}/chunks`);
        const data = await response.json();
        
        if (data.success) {
            displayDocumentChunks(data.data, docId);
        } else {
            showNotification('Error loading chunks: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error loading chunks:', error);
        showNotification('Error loading document chunks', 'error');
    } finally {
        showLoading(false);
    }
}

// Display document chunks in modal
function displayDocumentChunks(chunks, docId) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Document Chunks (${chunks.length} total)</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" style="max-height: 70vh; overflow-y: auto;">
                    ${chunks.length === 0 ? '<p class="text-muted">No chunks found</p>' : ''}
                    ${chunks.map((chunk, index) => `
                        <div class="card mb-3">
                            <div class="card-header">
                                <small class="text-muted">Chunk ${index + 1}</small>
                            </div>
                            <div class="card-body">
                                <p class="card-text">${chunk.content}</p>
                            </div>
                        </div>
                    `).join('')}
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    // Remove modal from DOM when hidden
    modal.addEventListener('hidden.bs.modal', () => {
        modal.remove();
    });
}

// Auto-refresh functionality
let autoRefreshInterval;

function startAutoRefresh() {
    autoRefreshInterval = setInterval(() => {
        if (document.getElementById('bots-section').style.display !== 'none') {
            loadBotStatuses();
        }
    }, 30000); // Refresh every 30 seconds
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
}

// Start auto-refresh when page loads
document.addEventListener('DOMContentLoaded', function() {
    startAutoRefresh();
});

// Stop auto-refresh when page unloads
window.addEventListener('beforeunload', function() {
    stopAutoRefresh();
});

