


<style scoped>
/* Structure et layout */
.equipe-node {
  margin: 0.25rem 0;
}

.node-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.node-content:hover {
  background: #f8f9fa;
  border-color: #e9ecef;
}

.node-content.selected {
  background: #e8f4fc;
  border-color: #3498db;
  box-shadow: 0 2px 4px rgba(52, 152, 219, 0.1);
}

.node-content.inactive {
  opacity: 0.6;
  background: #f9f9f9;
}

.equipe-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.equipe-name {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.95rem;
  margin-bottom: 0.15rem;
}

.pole-info {
  font-size: 0.8rem;
  color: #6c757d;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.separator {
  color: #dee2e6;
  margin: 0 0.25rem;
}

/* Boutons et interactions */
.expand-btn, .btn-refresh, .btn-edit, .close-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  border-radius: 4px;
  transition: all 0.2s;
}

.expand-btn:hover, .btn-refresh:hover, .btn-edit:hover, .close-btn:hover {
  background: #e9ecef;
  color: #495057;
}

.expand-placeholder {
  width: 28px;
}

.btn-refresh {
  width: 32px;
  height: 32px;
  border: 1px solid #dee2e6;
  background: white;
}

.btn-edit, .close-btn {
  background: #f8f9fa;
}


.manager-info, .membres-btn, .btn-status {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.6rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  white-space: nowrap;
  transition: all 0.2s;
}

.manager-info {
  background: #f8f9fa;
}

.manager-label {
  color: #6c757d;
  font-weight: 500;
  white-space: nowrap;
}

.manager-name {
  color: #495057;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.manager-matricule {
  font-family: monospace;
  color: #3498db;
  font-weight: 600;
  font-size: 0.8rem;
  background: #e8f4fc;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  white-space: nowrap;
}

.membres-btn {
  background: #f0f9f0;
  color: #27ae60;
  border: none;
  cursor: pointer;
}

.membres-btn:hover {
  background: #e1f7e1;
  transform: scale(1.05);
}

.membres-btn:active {
  transform: scale(0.95);
}

.membres-btn.active {
  background: #27ae60;
  color: white;
}

.membres-count {
  font-weight: 600;
}

.btn-status {
  border: none;
  cursor: pointer;
}

.btn-status.active {
  background: #f0f9f0;
  color: #27ae60;
}

.btn-status.active:hover {
  background: #e1f7e1;
}

.btn-status.inactive {
  background: #f8f9fa;
  color: #6c757d;
}

.btn-status.inactive:hover {
  background: #e9ecef;
}

.status-text {
  font-size: 0.8rem;
}

/* Liste des membres */
.membres-list, .membres-section {
  margin: 0.5rem 0 0.5rem 2rem;
  padding: 1rem;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  animation: slideDown 0.3s ease-out;
}

.membres-header, .membres-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e9ecef;
}

.membres-header h4, .membres-list-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 0.9rem;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.membre-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 6px;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.membre-item:hover {
  background: #e9ecef;
  border-color: #dee2e6;
  transform: translateY(-2px);
}

.membre-item.is-manager {
  background: #fff8e1;
  border-color: #ffd54f;
}

.membre-avatar {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #3498db;
  color: white;
  border-radius: 50%;
  font-size: 1.2rem;
}

.membre-avatar.manager {
  background: #f39c12;
}

.membre-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.membre-name-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.15rem;
}

.membre-name {
  font-weight: 500;
  color: #2c3e50;
  font-size: 0.85rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.manager-badge {
  font-size: 0.7rem;
  background: #f39c12;
  color: white;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
}

.membre-matricule {
  font-family: monospace;
  font-size: 0.75rem;
  color: #6c757d;
  font-weight: 600;
}


/* Animations et états */
@keyframes slideDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.loading-membres {
  text-align: center;
  padding: 1rem;
  color: #6c757d;
}

.empty-membres {
  text-align: center;
  padding: 1rem;
  color: #6c757d;
  font-style: italic;
}

.children {
  border-left: 2px solid #e9ecef;
  margin-left: 1rem;
  padding-left: 0.75rem;
}

/* Grilles */
.membres-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.75rem;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

/* Responsive */
@media (max-width: 1024px) {
  .node-content {
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .manager-info, .membres-btn, .btn-status {
    order: 1;
  }

  .equipe-info {
    width: 100%;
  }

  .membres-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
}

@media (max-width: 768px) {
  .node-content {
    padding: 0.5rem;
  }

  .manager-info {
    flex-wrap: wrap;
  }

  .status-text {
    display: none;
  }

  .btn-status {
    padding: 0.35rem;
  }

  .membres-list {
    margin-left: 1rem;
    padding: 0.75rem;
  }

  .membres-grid {
    grid-template-columns: 1fr;
  }
}
</style>