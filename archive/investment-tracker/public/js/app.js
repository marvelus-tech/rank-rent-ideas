// ===== Investment Tracker App =====

const API_URL = '';
let currentTab = 'stocks';
let currentItems = [];
let editingItem = null;

// Tab configuration
const tabs = {
  stocks: { label: 'Stocks', icon: 'trending-up' },
  crypto: { label: 'Crypto', icon: 'zap' },
  niches: { label: 'Niches', icon: 'target' },
  models: { label: 'Models', icon: 'box' },
  insights: { label: 'Insights', icon: 'eye' }
};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initEventListeners();
  loadItems(currentTab);
});

// ===== Tab Navigation =====
function initTabs() {
  const tabButtons = document.querySelectorAll('.tab-btn');
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const tab = btn.dataset.tab;
      switchTab(tab);
    });
  });
}

function switchTab(tab) {
  currentTab = tab;
  
  // Update active tab
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tab);
  });
  
  // Show grid view, hide detail view
  document.getElementById('grid-view').classList.remove('hidden');
  document.getElementById('detail-view').classList.add('hidden');
  
  // Load items
  loadItems(tab);
}

// ===== Event Listeners =====
function initEventListeners() {
  // Search
  document.getElementById('search-input').addEventListener('input', (e) => {
    filterItems(e.target.value, document.getElementById('status-filter').value);
  });
  
  // Status filter
  document.getElementById('status-filter').addEventListener('change', (e) => {
    filterItems(document.getElementById('search-input').value, e.target.value);
  });
  
  // Add item
  document.getElementById('add-item-btn').addEventListener('click', () => {
    openModal();
  });
  
  // Modal close
  document.getElementById('modal-close').addEventListener('click', closeModal);
  document.getElementById('modal-cancel').addEventListener('click', closeModal);
  
  // Form submit
  document.getElementById('item-form').addEventListener('submit', handleFormSubmit);
  
  // Back button
  document.getElementById('back-btn').addEventListener('click', () => {
    document.getElementById('grid-view').classList.remove('hidden');
    document.getElementById('detail-view').classList.add('hidden');
  });
  
  // Edit button
  document.getElementById('edit-btn').addEventListener('click', () => {
    if (editingItem) {
      openModal(editingItem);
    }
  });
  
  // Delete button
  document.getElementById('delete-btn').addEventListener('click', async () => {
    if (editingItem && confirm('Delete this item?')) {
      await deleteItem(editingItem.id);
      document.getElementById('grid-view').classList.remove('hidden');
      document.getElementById('detail-view').classList.add('hidden');
      loadItems(currentTab);
    }
  });
  
  // Presentation mode
  document.getElementById('presentation-toggle').addEventListener('click', togglePresentation);
}

// ===== API Calls =====
async function loadItems(category) {
  try {
    const response = await fetch(`${API_URL}/api/${category}`);
    const data = await response.json();
    currentItems = data.items || [];
    renderItems(currentItems);
  } catch (error) {
    console.error('Error loading items:', error);
    renderItems([]);
  }
}

async function addItem(item) {
  const response = await fetch(`${API_URL}/api/${currentTab}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(item)
  });
  return response.json();
}

async function updateItem(id, item) {
  const response = await fetch(`${API_URL}/api/${currentTab}/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(item)
  });
  return response.json();
}

async function deleteItem(id) {
  await fetch(`${API_URL}/api/${currentTab}/${id}`, {
    method: 'DELETE'
  });
}

async function loadObsidianNote(path) {
  try {
    const response = await fetch(`${API_URL}/api/note/${path}`);
    const data = await response.json();
    return data.html;
  } catch (error) {
    return '<p>Note not found</p>';
  }
}

// ===== Rendering =====
function renderItems(items) {
  const grid = document.getElementById('items-grid');
  
  if (items.length === 0) {
    grid.innerHTML = `
      <div class="empty-state">
        <p>No items yet. Click "+ Add Item" to get started.</p>
      </div>
    `;
    return;
  }
  
  grid.innerHTML = items.map(item => createCardHTML(item)).join('');
  
  // Add click handlers
  document.querySelectorAll('.item-card').forEach(card => {
    card.addEventListener('click', () => {
      const itemId = card.dataset.id;
      const item = currentItems.find(i => i.id === itemId);
      if (item) {
        showDetail(item);
      }
    });
  });
}

function createCardHTML(item) {
  const statusClass = `status-${item.status}`;
  const tagsHtml = item.tags?.map(tag => `<span class="tag">${tag}</span>`).join('') || '';
  
  return `
    <div class="item-card" data-id="${item.id}">
      <div class="card-header">
        <div>
          <div class="card-title">${item.name}</div>
          ${item.ticker ? `<div class="card-ticker">${item.ticker}</div>` : ''}
        </div>
        <span class="status-badge ${statusClass}">${item.status}</span>
      </div>
      ${item.price ? `<div class="card-price">${item.price}</div>` : ''}
      <div class="card-tags">${tagsHtml}</div>
      ${item.notes ? `<div class="card-notes">${item.notes}</div>` : ''}
      <div class="card-footer">
        <span>${item.added || ''}</span>
        ${item.obsidianNote ? `
          <a href="#" class="card-obsidian-link" onclick="event.stopPropagation()">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
              <polyline points="15 3 21 3 21 9"></polyline>
              <line x1="10" y1="14" x2="21" y2="3"></line>
            </svg>
            Obsidian
          </a>
        ` : ''}
      </div>
    </div>
  `;
}

async function showDetail(item) {
  editingItem = item;
  
  document.getElementById('grid-view').classList.add('hidden');
  document.getElementById('detail-view').classList.remove('hidden');
  
  const detailContent = document.getElementById('detail-content');
  
  // Load Obsidian note if available
  let obsidianHtml = '<p>No Obsidian note linked</p>';
  if (item.obsidianNote) {
    obsidianHtml = await loadObsidianNote(item.obsidianNote);
  }
  
  const tagsHtml = item.tags?.map(tag => `<span class="tag">${tag}</span>`).join('') || '';
  const statusClass = `status-${item.status}`;
  
  detailContent.innerHTML = `
    <div class="detail-main">
      <div class="card-header" style="margin-bottom: 1.5rem;">
        <div>
          <h1 style="font-size: 1.75rem; margin-bottom: 0.5rem;">${item.name}</h1>
          ${item.ticker ? `<div class="card-ticker" style="font-size: 1rem;">${item.ticker}</div>` : ''}
        </div>
        <span class="status-badge ${statusClass}">${item.status}</span>
      </div>
      
      ${item.price ? `<div class="card-price" style="font-size: 2rem; margin-bottom: 1.5rem;">${item.price}</div>` : ''}
      
      <div class="card-tags" style="margin-bottom: 1.5rem;">${tagsHtml}</div>
      
      ${item.notes ? `
        <div style="margin-bottom: 1.5rem;">
          <h3 style="font-size: 1rem; color: var(--text-secondary); margin-bottom: 0.75rem;">Notes</h3>
          <p style="color: var(--text-secondary); line-height: 1.7;">${item.notes}</p>
        </div>
      ` : ''}
      
      <div style="margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid var(--border-color);">
        <h3 style="font-size: 1rem; color: var(--text-secondary); margin-bottom: 1rem;">Quick Stats</h3>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
          <div class="sidebar-section" style="padding: 1rem;">
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.25rem;">Status</div>
            <div style="font-weight: 600;">${item.status}</div>
          </div>
          <div class="sidebar-section" style="padding: 1rem;">
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.25rem;">Added</div>
            <div style="font-weight: 600;">${item.added || 'N/A'}</div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="detail-sidebar">
      <div class="sidebar-section">
        <div class="sidebar-title">Obsidian Notes</div>
        <div class="obsidian-content">${obsidianHtml}</div>
      </div>
      
      ${item.obsidianNote ? `
        <div class="sidebar-section">
          <div class="sidebar-title">Linked Note</div>
          <a href="obsidian://open?vault=Penelopi&file=${encodeURIComponent(item.obsidianNote.replace('.md', ''))}" 
             class="card-obsidian-link" 
             style="font-size: 0.875rem;">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
              <polyline points="15 3 21 3 21 9"></polyline>
              <line x1="10" y1="14" x2="21" y2="3"></line>
            </svg>
            Open in Obsidian
          </a>
        </div>
      ` : ''}
    </div>
  `;
}

// ===== Filtering =====
function filterItems(search, status) {
  let filtered = currentItems;
  
  if (search) {
    const searchLower = search.toLowerCase();
    filtered = filtered.filter(item => 
      item.name?.toLowerCase().includes(searchLower) ||
      item.ticker?.toLowerCase().includes(searchLower) ||
      item.notes?.toLowerCase().includes(searchLower) ||
      item.tags?.some(tag => tag.toLowerCase().includes(searchLower))
    );
  }
  
  if (status !== 'all') {
    filtered = filtered.filter(item => item.status === status);
  }
  
  renderItems(filtered);
}

// ===== Modal =====
function openModal(item = null) {
  const modal = document.getElementById('modal');
  const title = document.getElementById('modal-title');
  const form = document.getElementById('item-form');
  
  if (item) {
    title.textContent = 'Edit Item';
    document.getElementById('item-id').value = item.id;
    document.getElementById('item-name').value = item.name || '';
    document.getElementById('item-ticker').value = item.ticker || '';
    document.getElementById('item-status').value = item.status || 'researching';
    document.getElementById('item-price').value = item.price || '';
    document.getElementById('item-tags').value = item.tags?.join(', ') || '';
    document.getElementById('item-notes').value = item.notes || '';
    document.getElementById('item-obsidian').value = item.obsidianNote || '';
  } else {
    title.textContent = 'Add Item';
    form.reset();
    document.getElementById('item-id').value = '';
  }
  
  modal.classList.remove('hidden');
}

function closeModal() {
  document.getElementById('modal').classList.add('hidden');
  editingItem = null;
}

async function handleFormSubmit(e) {
  e.preventDefault();
  
  const id = document.getElementById('item-id').value;
  const item = {
    name: document.getElementById('item-name').value,
    ticker: document.getElementById('item-ticker').value,
    status: document.getElementById('item-status').value,
    price: document.getElementById('item-price').value,
    tags: document.getElementById('item-tags').value.split(',').map(t => t.trim()).filter(Boolean),
    notes: document.getElementById('item-notes').value,
    obsidianNote: document.getElementById('item-obsidian').value
  };
  
  if (id) {
    await updateItem(id, item);
  } else {
    await addItem(item);
  }
  
  closeModal();
  loadItems(currentTab);
}

// ===== Presentation Mode =====
function togglePresentation() {
  document.body.classList.toggle('presentation-mode');
  const btn = document.getElementById('presentation-toggle');
  const isPresenting = document.body.classList.contains('presentation-mode');
  btn.innerHTML = isPresenting ? `
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <line x1="18" y1="6" x2="6" y2="18"></line>
      <line x1="6" y1="6" x2="18" y2="18"></line>
    </svg>
    Exit
  ` : `
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
      <line x1="8" y1="21" x2="16" y2="21"></line>
      <line x1="12" y1="17" x2="12" y2="21"></line>
    </svg>
    Present
  `;
}
