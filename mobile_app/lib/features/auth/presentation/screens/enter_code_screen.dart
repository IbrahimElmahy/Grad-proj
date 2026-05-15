import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:gradiuationg_project/core/widgets/custom_text_field.dart';
import 'package:gradiuationg_project/core/widgets/primary_button.dart';


class EnterCodeScreen extends StatefulWidget {
  const EnterCodeScreen({super.key});

  @override
  State<EnterCodeScreen> createState() => _EnterCodeScreenState();
}

class _EnterCodeScreenState extends State<EnterCodeScreen> {
  final TextEditingController _tokenController = TextEditingController();
  String _email = '';
  String _backendToken = '';
  bool _loadedArgs = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_loadedArgs) return;
    final args = ModalRoute.of(context)?.settings.arguments;
    if (args is Map) {
      _email = args['email'] as String? ?? '';
      _backendToken = args['token'] as String? ?? '';
      _tokenController.text = _backendToken;
    }
    _loadedArgs = true;
  }

  @override
  void dispose() {
    _tokenController.dispose();
    super.dispose();
  }

  void _continue() {
    final token = _tokenController.text.trim();
    if (token.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter the reset token.')),
      );
      return;
    }

    Navigator.pushNamed(
      context,
      "/create-password",
      arguments: {
        'email': _email,
        'token': token,
      },
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
                "Enter Code",
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1B233A),
                ),
              ),
              const SizedBox(height: 12),
              const Text(
                "Enter the reset token generated for your account.",
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w400,
                  color: Color(0xFF6C757D),
                  height: 1.5,
                ),
              ),
              if (_email.isNotEmpty) ...[
                const SizedBox(height: 8),
                Text(
                  _email,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF1D55E5),
                  ),
                ),
              ],
              const SizedBox(height: 48),

              CustomTextField(
                controller: _tokenController,
                hintText: "Reset Token",
                prefixIcon: Icons.key_outlined,
              ),
              if (_backendToken.isNotEmpty) ...[
                const SizedBox(height: 10),
                const Text(
                  "Demo backend returns the token directly until email/SMS delivery is added.",
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 12,
                    color: Color(0xFF6C757D),
                    height: 1.4,
                  ),
                ),
              ],
              const SizedBox(height: 48),

              // Verify Button
              PrimaryButton(
                text: "Verify code",
                onPressed: _continue,
              ),
              const SizedBox(height: 24),

              // Resend text
              Center(
                child: RichText(
                  text: TextSpan(
                    text: "Didn't receive a code? ",
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w400,
                      color: Color(0xFF1B233A),
                    ),
                    children: [
                      TextSpan(
                        text: "Send again",
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
            ],
          ),
        ),
      ),
    );
  }
}
