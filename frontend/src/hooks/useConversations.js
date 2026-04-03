/**
 * useConversations hook — manages conversation list and CRUD.
 */

import { useState, useEffect, useCallback } from 'react';
import { getConversations, getConversation, deleteConversation } from '../services/api';

export default function useConversations() {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchConversations = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getConversations();
      setConversations(data);
    } catch {
      // Backend might not be running yet — that's fine
      console.warn('Could not fetch conversations (backend may be offline)');
    } finally {
      setLoading(false);
    }
  }, []);

  const loadConversation = useCallback(async (id) => {
    try {
      const data = await getConversation(id);
      return data;
    } catch (err) {
      console.error('Failed to load conversation:', err);
      return null;
    }
  }, []);

  const removeConversation = useCallback(async (id) => {
    try {
      await deleteConversation(id);
      setConversations(prev => prev.filter(c => c.id !== id));
      return true;
    } catch (err) {
      console.error('Failed to delete conversation:', err);
      return false;
    }
  }, []);

  // Fetch on mount
  useEffect(() => {
    fetchConversations();
  }, [fetchConversations]);

  return {
    conversations,
    loading,
    fetchConversations,
    loadConversation,
    removeConversation,
  };
}
