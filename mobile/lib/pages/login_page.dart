import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/provider_manager.dart';
import '../widgets/debug_config_widget.dart';
import '../widgets/google_sign_in_button.dart';
import 'forgot_password_page.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  // Controllers
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _usernameController = TextEditingController();

  // State
  bool _isLogin = true;
  bool _isLoading = false;
  bool _isGoogleLoading = false;
  String? _errorMessage;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    _usernameController.dispose();
    super.dispose();
  }

  // ========== AUTH LOGIC ==========

  Future<void> _handleSubmit() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final authProvider = Provider.of<AuthProvider>(context, listen: false);

    bool success;

    if (_isLogin) {
      success = await _performLogin(authProvider);
    } else {
      success = await _performRegistration(authProvider);
    }

    if (!mounted) return;

    setState(() => _isLoading = false);

    if (success) {
      await ProviderManager.onLogin(context);
      if (mounted) {
        Navigator.of(context).pushReplacementNamed('/home');
      }
    } else {
      setState(() {
        _errorMessage = authProvider.error ??
          (_isLogin ? 'Login failed' : 'Registration failed');
      });
    }
  }

  Future<bool> _performLogin(AuthProvider authProvider) async {
    return await authProvider.login(
      _emailController.text.trim(),
      _passwordController.text.trim(),
    );
  }

  Future<bool> _performRegistration(AuthProvider authProvider) async {
    return await authProvider.register(
      username: _usernameController.text.trim(),
      email: _emailController.text.trim(),
      password: _passwordController.text.trim(),
      confirmPassword: _confirmPasswordController.text.trim(),
    );
  }

  Future<void> _handleGoogleSignIn() async {
    final navigator = Navigator.of(context);
    final authProvider = Provider.of<AuthProvider>(context, listen: false);

    setState(() => _isGoogleLoading = true);

    final success = await authProvider.loginWithGoogle();

    if (!mounted) return;
    setState(() => _isGoogleLoading = false);

    if (success) {
      await ProviderManager.onLogin(context);
      if (mounted) {
        navigator.pushReplacementNamed('/home');
      }
    } else {
      setState(() {
        _errorMessage = authProvider.error ?? 'Google sign-in failed';
      });
    }
  }

  void _toggleMode() {
    setState(() {
      _isLogin = !_isLogin;
      _errorMessage = null;
      _formKey.currentState?.reset();
    });
  }

  // ========== UI BUILDERS ==========

  @override
  Widget build(BuildContext context) {
    return DebugConfigWidget(
      child: Scaffold(
        body: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SizedBox(height: 40),
                  _buildHeader(),
                  const SizedBox(height: 48),
                  _buildFormFields(),
                  const SizedBox(height: 24),
                  _buildSubmitButton(),
                  if (_isLogin) _buildForgotPasswordButton(),
                  const SizedBox(height: 16),
                  _buildGoogleSignInButton(),
                  if (_errorMessage != null) _buildErrorMessage(),
                  const SizedBox(height: 24),
                  _buildToggleModeButton(),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Column(
      children: [
        Semantics(
          header: true,
          child: const Text(
            'AREA',
            style: TextStyle(
              fontSize: 48,
              fontWeight: FontWeight.bold,
              color: Colors.blue,
            ),
            textAlign: TextAlign.center,
          ),
        ),
        const SizedBox(height: 8),
        const Text(
          'Automate your tasks',
          style: TextStyle(fontSize: 16, color: Colors.grey),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildFormFields() {
    return Column(
      children: [
        if (!_isLogin) ...[
          _buildUsernameField(),
          const SizedBox(height: 16),
        ],
        _buildEmailField(),
        const SizedBox(height: 16),
        _buildPasswordField(),
        if (!_isLogin) ...[
          const SizedBox(height: 16),
          _buildConfirmPasswordField(),
        ],
      ],
    );
  }

  Widget _buildUsernameField() {
    return Semantics(
      label: 'Username input field',
      hint: 'Enter your username',
      child: TextFormField(
        controller: _usernameController,
        decoration: const InputDecoration(
          labelText: 'Username',
          border: OutlineInputBorder(),
          prefixIcon: Icon(Icons.account_circle),
        ),
        textInputAction: TextInputAction.next,
        validator: (value) {
          if (value == null || value.isEmpty) {
            return 'Please enter a username';
          }
          if (value.length < 3) {
            return 'Username must be at least 3 characters';
          }
          if (!RegExp(r'^[a-zA-Z0-9_]+$').hasMatch(value)) {
            return 'Username can only contain letters, numbers, and underscores';
          }
          return null;
        },
      ),
    );
  }

  Widget _buildEmailField() {
    return Semantics(
      label: 'Email address input field',
      hint: 'Enter your email address',
      child: TextFormField(
        controller: _emailController,
        decoration: const InputDecoration(
          labelText: 'Email',
          border: OutlineInputBorder(),
          prefixIcon: Icon(Icons.email),
        ),
        keyboardType: TextInputType.emailAddress,
        textInputAction: TextInputAction.next,
        validator: (value) {
          if (value == null || value.isEmpty) {
            return 'Please enter your email';
          }
          if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value)) {
            return 'Please enter a valid email';
          }
          return null;
        },
      ),
    );
  }

  Widget _buildPasswordField() {
    return Semantics(
      label: 'Password input field',
      hint: 'Enter your password',
      child: TextFormField(
        controller: _passwordController,
        decoration: const InputDecoration(
          labelText: 'Password',
          border: OutlineInputBorder(),
          prefixIcon: Icon(Icons.lock),
        ),
        obscureText: true,
        textInputAction: TextInputAction.done,
        onFieldSubmitted: (_) => _handleSubmit(),
        validator: (value) {
          if (value == null || value.isEmpty) {
            return 'Please enter your password';
          }
          if (value.length < 8) {
            return 'Password must be at least 8 characters';
          }
          return null;
        },
      ),
    );
  }

  Widget _buildConfirmPasswordField() {
    return Semantics(
      label: 'Confirm password input field',
      hint: 'Re-enter your password',
      child: TextFormField(
        controller: _confirmPasswordController,
        decoration: const InputDecoration(
          labelText: 'Confirm Password',
          border: OutlineInputBorder(),
          prefixIcon: Icon(Icons.lock_outline),
        ),
        obscureText: true,
        textInputAction: TextInputAction.done,
        onFieldSubmitted: (_) => _handleSubmit(),
        validator: (value) {
          if (value == null || value.isEmpty) {
            return 'Please confirm your password';
          }
          if (value != _passwordController.text) {
            return 'Passwords do not match';
          }
          return null;
        },
      ),
    );
  }

  Widget _buildSubmitButton() {
    return Semantics(
      label: '${_isLogin ? 'Login' : 'Register'} button',
      hint: 'Tap to ${_isLogin ? 'sign in' : 'create account'}',
      child: SizedBox(
        height: 50,
        child: ElevatedButton(
          onPressed: _isLoading ? null : _handleSubmit,
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.blue,
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
          child: _isLoading
              ? const SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                  ),
                )
              : Text(
                  _isLogin ? 'Sign In' : 'Create Account',
                  style: const TextStyle(fontSize: 16),
                ),
        ),
      ),
    );
  }

  Widget _buildForgotPasswordButton() {
    return Align(
      alignment: Alignment.centerRight,
      child: TextButton(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => const ForgotPasswordPage(),
            ),
          );
        },
        child: const Text(
          'Forgot password ?',
          style: TextStyle(
            color: Colors.blue,
            fontSize: 14,
          ),
        ),
      ),
    );
  }

  Widget _buildGoogleSignInButton() {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, _) {
        return GoogleSignInButton(
          isLoading: _isGoogleLoading,
          onPressed: _handleGoogleSignIn,
        );
      },
    );
  }

  Widget _buildErrorMessage() {
    return Semantics(
      label: 'Error message',
      child: Container(
        margin: const EdgeInsets.only(top: 16),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.red.shade50,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Colors.red.shade200),
        ),
        child: Row(
          children: [
            Icon(Icons.error_outline, color: Colors.red.shade700, size: 20),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                _errorMessage!,
                style: TextStyle(color: Colors.red.shade700),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildToggleModeButton() {
    return Semantics(
      label: 'Switch to ${_isLogin ? 'register' : 'login'} mode',
      child: TextButton(
        onPressed: _toggleMode,
        child: RichText(
          text: TextSpan(
            style: const TextStyle(color: Colors.grey),
            children: [
              TextSpan(
                text: _isLogin
                    ? "Don't have an account? "
                    : "Already have an account? ",
              ),
              TextSpan(
                text: _isLogin ? 'Sign Up' : 'Sign In',
                style: const TextStyle(
                  color: Colors.blue,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
