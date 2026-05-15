import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:gradiuationg_project/core/widgets/custom_text_field.dart';
import 'package:gradiuationg_project/core/widgets/primary_button.dart';
import '../../data/auth_service.dart';


class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final _emailController = TextEditingController();
  final AuthService _authService = const AuthService();
  bool _isLoading = false;

  @override
  void dispose() {
    _emailController.dispose();
    super.dispose();
  }

  Future<void> _requestReset() async {
    final email = _emailController.text.trim();
    if (email.isEmpty) {
      _showMessage('Please enter your email address.');
      return;
    }

    setState(() => _isLoading = true);
    try {
      final request = await _authService.forgotPassword(email);
      if (!mounted) return;
      Navigator.pushNamed(
        context,
        "/enter-code",
        arguments: {
          'email': request.email,
          'token': request.token,
        },
      );
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
                "Forget Password",
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1B233A),
                ),
              ),
              const SizedBox(height: 12),
              const Text(
                "Enter the email associated with your account.",
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w400,
                  color: Color(0xFF6C757D),
                  height: 1.5,
                ),
              ),
              const SizedBox(height: 48),

              // Email Field
              CustomTextField(
                controller: _emailController,
                hintText: "Email Address",
                prefixIcon: Icons.email_outlined,
                keyboardType: TextInputType.emailAddress,
              ),
              const SizedBox(height: 24),

              // Remember password text
              Center(
                child: RichText(
                  text: TextSpan(
                    text: "Remember your password? ",
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w400,
                      color: Color(0xFF1B233A),
                    ),
                    children: [
                      TextSpan(
                        text: "Sign In",
                        style: const TextStyle(
                          color: Color(0xFF1D55E5),
                          fontWeight: FontWeight.w600,
                        ),
                        recognizer: TapGestureRecognizer()
                          ..onTap = () {
                            Navigator.pop(context);
                          },
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 32),

              // Reset Password Button
              PrimaryButton(
                text: "Reset Password",
                isLoading: _isLoading,
                onPressed: _requestReset,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
