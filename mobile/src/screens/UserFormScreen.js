import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, Alert, KeyboardAvoidingView, Platform } from 'react-native';
import {
  Button,
  TextInput,
  Title,
  Text,
  ActivityIndicator,
  Divider,
  RadioButton
} from 'react-native-paper';

const API_URL = 'http://10.172.116.56:8080';

const UserFormScreen = ({ route, navigation }) => {
  const { mode, userId } = route.params || { mode: 'add' };

  const [user, setUser] = useState({
    username: '',
    email: '',
    role: 'user'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fetching, setFetching] = useState(mode === 'edit');

  useEffect(() => {
    if (mode === 'edit' && userId) {
      fetchUser(userId);
    }
  }, [userId, mode]);

  const fetchUser = async (id) => {
    setFetching(true);
    try {
      const response = await fetch(`${API_URL}/api/users/${id}`);

      if (!response.ok) {
        throw new Error('Failed to fetch user data');
      }

      const data = await response.json();
      setUser(data);
    } catch (err) {
      console.error('Error fetching user:', err);
      setError(err.message);
      Alert.alert('Error', 'Failed to load user data');
    } finally {
      setFetching(false);
    }
  };

  const handleChange = (name, value) => {
    setUser({ ...user, [name]: value });
  };

  const validateForm = () => {
    if (!user.username || !user.email) {
      Alert.alert('Validation Error', 'Username and email are required');
      return false;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(user.email)) {
      Alert.alert('Validation Error', 'Please enter a valid email address');
      return false;
    }

    return true;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    setLoading(true);
    setError(null);

    try {
      const url = mode === 'add'
        ? `${API_URL}/api/users`
        : `${API_URL}/api/users/${userId}`;

      const method = mode === 'add' ? 'POST' : 'PUT';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(user),
      });

      if (!response.ok) {
        throw new Error('Failed to save user');
      }

      Alert.alert(
        'Success',
        `User ${mode === 'add' ? 'created' : 'updated'} successfully`,
        [{ text: 'OK', onPress: () => navigation.navigate('UserList') }]
      );
    } catch (err) {
      console.error('Error saving user:', err);
      setError(err.message);
      Alert.alert('Error', `Failed to ${mode === 'add' ? 'create' : 'update'} user`);
    } finally {
      setLoading(false);
    }
  };

  if (fetching) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#6366F1" />
        <Text style={styles.loadingText}>Loading user data...</Text>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Title style={styles.title}>
          {mode === 'add' ? 'Add New User' : 'Edit User'}
        </Title>

        {error && (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>{error}</Text>
          </View>
        )}

        <TextInput
          label="Username"
          value={user.username}
          onChangeText={(value) => handleChange('username', value)}
          style={styles.input}
          mode="outlined"
          autoCapitalize="none"
        />

        <TextInput
          label="Email"
          value={user.email}
          onChangeText={(value) => handleChange('email', value)}
          style={styles.input}
          mode="outlined"
          keyboardType="email-address"
          autoCapitalize="none"
        />

        <Text style={styles.label}>Role</Text>
        <RadioButton.Group
          onValueChange={(value) => handleChange('role', value)}
          value={user.role}
        >
          <View style={styles.radioOption}>
            <RadioButton value="user" />
            <Text>User</Text>
          </View>
          <View style={styles.radioOption}>
            <RadioButton value="admin" />
            <Text>Admin</Text>
          </View>
        </RadioButton.Group>

        <Divider style={styles.divider} />

        <View style={styles.buttonContainer}>
          <Button
            mode="contained"
            onPress={handleSubmit}
            loading={loading}
            style={styles.submitButton}
            disabled={loading}
          >
            {loading ? 'Saving...' : 'Save'}
          </Button>

          <Button
            mode="outlined"
            onPress={() => navigation.goBack()}
            style={styles.cancelButton}
            disabled={loading}
          >
            Cancel
          </Button>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
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
  scrollContent: {
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
    color: '#4F46E5',
  },
  input: {
    marginBottom: 16,
    backgroundColor: 'white',
  },
  label: {
    fontSize: 16,
    marginBottom: 8,
    color: '#4B5563',
  },
  radioOption: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  divider: {
    marginVertical: 16,
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  submitButton: {
    flex: 1,
    marginRight: 8,
    backgroundColor: '#6366F1',
  },
  cancelButton: {
    flex: 1,
    marginLeft: 8,
    borderColor: '#6B7280',
  },
  errorContainer: {
    backgroundColor: '#FEE2E2',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  errorText: {
    color: '#DC2626',
  },
});

export default UserFormScreen;
