import React, { useState, useEffect } from 'react';
import { View, StyleSheet, FlatList, Alert } from 'react-native';
import {
  Button,
  Card,
  Title,
  Paragraph,
  Text,
  ActivityIndicator,
  Chip,
  Portal,
  Dialog,
  FAB
} from 'react-native-paper';
import { useFocusEffect } from '@react-navigation/native';

const API_URL = 'http://10.172.116.56:8080';

const UserListScreen = ({ navigation }) => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [confirmDelete, setConfirmDelete] = useState(null);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/users`);

      if (!response.ok) {
        throw new Error('Failed to fetch users');
      }

      const data = await response.json();
      setUsers(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching users:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useFocusEffect(
    React.useCallback(() => {
      fetchUsers();
    }, [])
  );

  const handleDeleteClick = (userId) => {
    setConfirmDelete(userId);
  };

  const confirmDeleteUser = async () => {
    if (!confirmDelete) return;

    try {
      const response = await fetch(`${API_URL}/api/users/${confirmDelete}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete user');
      }

      setUsers(users.filter(user => user.id !== confirmDelete));

      Alert.alert('Success', 'User deleted successfully');
    } catch (err) {
      console.error('Error deleting user:', err);
      Alert.alert('Error', err.message);
    } finally {
      setConfirmDelete(null);
    }
  };

  const renderUserItem = ({ item }) => (
    <Card style={styles.userCard}>
      <Card.Content>
        <View style={styles.userHeader}>
          <View>
            <Title>{item.username}</Title>
            <Paragraph>{item.email}</Paragraph>
          </View>
          <Chip
            mode="outlined"
            style={[
              styles.roleChip,
              item.role === 'admin' ? styles.adminChip : styles.userChip
            ]}
          >
            {item.role}
          </Chip>
        </View>
        <View style={styles.actions}>
          <Button
            mode="outlined"
            onPress={() => navigation.navigate('UserForm', { mode: 'edit', userId: item.id })}
            style={styles.actionButton}
          >
            Edit
          </Button>
          <Button
            mode="outlined"
            onPress={() => handleDeleteClick(item.id)}
            style={[styles.actionButton, styles.deleteButton]}
          >
            Delete
          </Button>
        </View>
      </Card.Content>
    </Card>
  );

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#6366F1" />
        <Text style={styles.loadingText}>Loading users...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorTitle}>Error!</Text>
        <Text style={styles.errorText}>{error}</Text>
        <Button
          mode="contained"
          onPress={fetchUsers}
          style={styles.retryButton}
        >
          Retry
        </Button>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Portal>
        <Dialog
          visible={confirmDelete !== null}
          onDismiss={() => setConfirmDelete(null)}
        >
          <Dialog.Title>Confirm Delete</Dialog.Title>
          <Dialog.Content>
            <Paragraph>Are you sure you want to delete this user? This action cannot be undone.</Paragraph>
          </Dialog.Content>
          <Dialog.Actions>
            <Button onPress={() => setConfirmDelete(null)}>Cancel</Button>
            <Button onPress={confirmDeleteUser} color="#DC2626">Delete</Button>
          </Dialog.Actions>
        </Dialog>
      </Portal>

      {users.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>No users found.</Text>
        </View>
      ) : (
        <FlatList
          data={users}
          renderItem={renderUserItem}
          keyExtractor={item => item.id.toString()}
          contentContainerStyle={styles.listContent}
        />
      )}

      <FAB
        style={styles.fab}
        icon="plus"
        onPress={() => navigation.navigate('UserForm', { mode: 'add' })}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F3F4F6',
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  loadingText: {
    marginTop: 8,
    fontSize: 16,
  },
  listContent: {
    padding: 16,
  },
  userCard: {
    marginBottom: 12,
    borderRadius: 8,
  },
  userHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  roleChip: {
    height: 28,
  },
  adminChip: {
    backgroundColor: '#E0E7FF',
    borderColor: '#6366F1',
  },
  userChip: {
    backgroundColor: '#DBEAFE',
    borderColor: '#3B82F6',
  },
  actions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    marginTop: 8,
  },
  actionButton: {
    marginLeft: 8,
  },
  deleteButton: {
    borderColor: '#DC2626',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#FEE2E2',
  },
  errorTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#DC2626',
    marginBottom: 8,
  },
  errorText: {
    fontSize: 16,
    marginBottom: 16,
    textAlign: 'center',
  },
  retryButton: {
    backgroundColor: '#6366F1',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  emptyText: {
    fontSize: 16,
    color: '#6B7280',
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
    backgroundColor: '#6366F1',
  },
});

export default UserListScreen;
