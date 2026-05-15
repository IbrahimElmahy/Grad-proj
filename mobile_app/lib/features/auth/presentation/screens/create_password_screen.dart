import 'package:flutter/material.dart';
import 'package:gradiuationg_project/core/widgets/custom_text_field.dart';
import 'package:gradiuationg_project/core/widgets/primary_button.dart';
import '../../data/auth_service.dart';


class CreatePasswordScreen extends StatefulWidget {
  const CreatePasswordScreen({super.key});

  @override
  State<CreatePasswordScreen> createState() => _CreatePasswordScreenState();
}

class _CreatePasswordScreenState extends State<CreatePasswordScreen> {
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final AuthService _authService = const AuthService();
  
  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;
  bool _isLoading = false;
  String _token = '';
  bool _loadedArgs = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_loadedArgs) return;
    final args = ModalRoute.of(context)?.settings.arguments;
    if (args is Map) {
      _token = args['token'] as String? ?? '';
    }
    _loadedArgs = true;
  }

  @override
  void dispose() {
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> _updatePassword() async {
    final password = _passwordController.text;
    final confirmPassword = _confirmPasswordController.text;

    if (_token.isEmpty) {
      _showMessage('Reset token is missing. Please request a new reset link.');
      return;
    }
    if (password.length < 12) {
      _showMessage('Password must be at least 12 characters.');
      return;
    }
    if (password != confirmPassword) {
      _showMessage('Passwords do not match.');
      return;
    }

    setState(() => _isLoading = true);
    try {
      await _authService.resetPassword(
        token: _token,
        password: password,
        passwordConfirm: confirmPassword,
      );
      if (!mounted) return;
      Navigator.pushNamedAndRemoveUntil(context, "/password-changed", (route) => false);
    } catch (error) {
      if (!mounted) return;
      _showMessage(error.toString());
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, color: Colors.black, size: 20),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                "Create Password",
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1B233A),
                ),
              ),
              const SizedBox(height: 12),
              const Text(
                "Create a new password. Ensure it differs\nfrom previous ones for security.",
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w400,
                  color: Color(0xFF6C757D),
                  height: 1.5,
                ),
              ),
              const SizedBox(height: 48),

              // Password Field
              CustomTextField(
                controller: _passwordController,
                hintText: "Password",
                prefixIcon: Icons.lock_outline,
                obscureText: _obscurePassword,
                suffixIcon: IconButton(
                  icon: Icon(
                    _obscurePassword ? Icons.visibility_off_outlined : Icons.visibility_outlined,
                    color: const Color(0xFF9E9E9E),
                    size: 20,
                  ),
                  onPressed: () {
                    setState(() {
                      _obscurePassword = !_obscurePassword;
                    });
                  },
                ),
              ),
              const SizedBox(height: 16),

              // Confirm Password Field
              CustomTextField(
                controller: _confirmPasswordController,
                hintText: "Confirm Password",
                prefixIcon: Icons.lock_outline,
                obscureText: _obscureConfirmPassword,
                suffixIcon: IconButton(
                  icon: Icon(
                    _obscureConfirmPassword ? Icons.visibility_off_outlined : Icons.visibility_outlined,
                    color: const Color(0xFF9E9E9E),
                    size: 20,
                  ),
                  onPressed: () {
                    setState(() {
                      _obscureConfirmPassword = !_obscureConfirmPassword;
                    });
                  },
                ),
              ),
              const SizedBox(height: 32),

              // Update Password Button
              PrimaryButton(
                text: "Update Password",
                isLoading: _isLoading,
                onPressed: _updatePassword,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
