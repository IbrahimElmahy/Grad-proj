import 'package:flutter/material.dart';
import 'package:gradiuationg_project/core/widgets/primary_button.dart';


class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key});

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
                onPressed: () {
                  // Demo account action
                },
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
                child: const Text(
                  "Continue With Demo Account",
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                ),
              ),

              Spacer(flex: 3), // Bottom padding
            ],
          ),
        ),
      ),
    );
  }
}
