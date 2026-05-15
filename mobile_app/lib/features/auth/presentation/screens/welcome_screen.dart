import 'package:flutter/material.dart';
import 'package:gradiuationg_project/core/widgets/primary_button.dart';
import 'package:gradiuationg_project/features/auth/data/auth_service.dart';


class WelcomeScreen extends StatefulWidget {
  const WelcomeScreen({super.key});

  @override
  State<WelcomeScreen> createState() => _WelcomeScreenState();
}

class _WelcomeScreenState extends State<WelcomeScreen> {
  final AuthService _authService = const AuthService();
  bool _isDemoLoading = false;

  Future<void> _continueWithDemo() async {
    setState(() => _isDemoLoading = true);
    try {
      await _authService.login(email: 'officer@rvms.com', password: 'officer123');
      if (!mounted) return;
      Navigator.pushNamedAndRemoveUntil(context, '/home', (route) => false);
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(error.toString())),
      );
    } finally {
      if (mounted) setState(() => _isDemoLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 40.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Spacer(flex: 2),

              // Logo and Title
              Center(
                child: Column(
                  children: [
                    Image.asset(
                      "assets/images/rvms_logo.png",
                      width: 306,
                      height: 306,
                      errorBuilder: (context, error, stackTrace) {
                        return const Icon(
                          Icons.security,
                          size: 100,
                          color: Color(0xFF1B233A),
                        );
                      },
                    ),

                    const Text(
                      "Runway Quick Check",
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w500,
                        color: Color(0xFF6C757D),
                      ),
                    ),
                  ],
                ),
              ),

              const Spacer(flex: 1),

              // Action Buttons
              PrimaryButton(
                text: "Log In",
                onPressed: () {
                  Navigator.pushNamed(context, "/login");
                },
              ),

              const SizedBox(height: 16),

              OutlinedButton(
                onPressed: _isDemoLoading ? null : _continueWithDemo,
                style: OutlinedButton.styleFrom(
                  foregroundColor: const Color(0xFF1B233A),
                  minimumSize: const Size(double.infinity, 56),
                  side: const BorderSide(color: Color(0xFFD6D9E0), width: 1.5),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(
                      30,
                    ), // Pill-shaped button
                  ),
                ),
                child: _isDemoLoading
                    ? const SizedBox(
                        height: 22,
                        width: 22,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text(
                        "Continue With Demo Account",
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                      ),
              ),

              const Spacer(flex: 3),
            ],
          ),
        ),
      ),
    );
  }
}
