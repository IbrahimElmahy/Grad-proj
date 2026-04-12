import 'package:flutter/material.dart';

class UserAvatar extends StatelessWidget {
  const UserAvatar({super.key, required this.imagePath});
  final String imagePath;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 44,
      height: 43,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(color: Colors.blue, width: 1),
      ),
      child: ClipOval(
        child: Image.asset(
          imagePath,
          fit: BoxFit.cover,
          errorBuilder: (context, error, stackTrace) {
            return Container(
              color: Colors.grey.shade200,
              child: const Icon(Icons.person, color: Colors.grey),
            );
          },
        ),
      ),
    );
  }
}
