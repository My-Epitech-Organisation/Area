import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { StatusBar } from 'expo-status-bar';
import { Provider as PaperProvider, DefaultTheme } from 'react-native-paper';

import HomeScreen from './src/screens/HomeScreen';
import UserListScreen from './src/screens/UserListScreen';
import UserFormScreen from './src/screens/UserFormScreen';

const Stack = createNativeStackNavigator();

const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#6366F1',
    accent: '#DB2777',
    background: '#F3F4F6',
    surface: '#FFFFFF',
  },
};

export default function App() {
  return (
    <PaperProvider theme={theme}>
      <NavigationContainer>
        <StatusBar style="light" />
        <Stack.Navigator
          initialRouteName="Home"
          screenOptions={{
            headerStyle: {
              backgroundColor: '#6366F1',
            },
            headerTintColor: '#fff',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
          }}
        >
          <Stack.Screen
            name="Home"
            component={HomeScreen}
            options={{ title: 'AREA Project' }}
          />
          <Stack.Screen
            name="UserList"
            component={UserListScreen}
            options={{ title: 'User Management' }}
          />
          <Stack.Screen
            name="UserForm"
            component={UserFormScreen}
            options={({ route }) => ({
              title: route.params?.mode === 'edit' ? 'Edit User' : 'Add User'
            })}
          />
        </Stack.Navigator>
      </NavigationContainer>
    </PaperProvider>
  );
}
