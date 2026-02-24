



<style scoped>
.demandes-container {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.demandes-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.demandes-header h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.3rem;
}

.btn-refresh {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-refresh:hover {
  background: #e9ecef;
}

.filters-bar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.8rem;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 20px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-chip:hover {
  background: #f8f9fa;
  border-color: #adb5bd;
}

.filter-chip.active {
  background: #e3f2fd;
  border-color: #3498db;
}

.color-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.count {
  background: rgba(0,0,0,0.1);
  padding: 0.1rem 0.4rem;
  border-radius: 12px;
  font-size: 0.7rem;
  margin-left: 0.25rem;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 3rem;
  color: #6c757d;
}

.loading-state i, .empty-state i {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.spinner {
  width: 30px;
  height: 30px;
  margin: 0 auto 1rem;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.demandes-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.demande-card {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.demande-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-color: #adb5bd;
}

.demande-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
  flex-shrink: 0;
}

.demande-icon.conge { background: #3498db; }
.demande-icon.retard { background: #f39c12; }
.demande-icon.permission { background: #27ae60; }
.demande-icon.repos_medical { background: #e74c3c; }
.demande-icon.ostie { background: #9b59b6; }

.demande-content {
  flex: 1;
  min-width: 0;
}

.demande-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.demande-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.demande-user {
  font-weight: 600;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.demande-type {
  font-size: 0.7rem;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  color: white;
  font-weight: 600;
  text-transform: uppercase;
}

.demande-type.conge { background: #3498db; }
.demande-type.retard { background: #f39c12; }
.demande-type.permission { background: #27ae60; }
.demande-type.repos_medical { background: #e74c3c; }
.demande-type.ostie { background: #9b59b6; }

.demande-date {
  color: #6c757d;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.demande-details {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.detail-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.2rem 0.6rem;
  background: #f8f9fa;
  border-radius: 16px;
  font-size: 0.75rem;
  color: #495057;
}

.detail-chip.motif {
  background: #e3f2fd;
  color: #1976d2;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.demande-actions {
  display: flex;
  gap: 0.25rem;
}

.action-btn {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  color: white;
  font-size: 0.9rem;
}

.action-btn.success { background: #27ae60; }
.action-btn.success:hover { background: #219a52; }

.action-btn.danger { background: #e74c3c; }
.action-btn.danger:hover { background: #c0392b; }

.action-btn.purple { background: #9b59b6; }
.action-btn.purple:hover { background: #8e44ad; }

.action-btn.warning { background: #f39c12; }
.action-btn.warning:hover { background: #e67e22; }

@media (max-width: 768px) {
  .demande-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .demande-date {
    align-self: flex-end;
  }
  
  .demande-actions {
    margin-top: 0.5rem;
  }
}
</style>