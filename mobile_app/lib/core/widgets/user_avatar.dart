import 'package:flutter/material.dart';
import '../network/api_config.dart';

class UserAvatar extends StatelessWidget {
  const UserAvatar({super.key, required this.imagePath, this.size = 44});
  final String? imagePath;
  final double size;

  @override
  Widget build(BuildContext context) {
    Widget imageWidget;
    final path = imagePath;

    if (path == null || path.isEmpty) {
      imageWidget = Container(
        color: Colors.grey.shade200,
        child: const Icon(Icons.person, color: Colors.grey),
      );
    } else if (path.startsWith('http') || path.startsWith('/media')) {
      final fullUrl = ApiConfig.absoluteMediaUrl(path);
      imageWidget = Image.network(
        fullUrl,
        fit: BoxFit.cover,
        errorBuilder: (context, error, stackTrace) {
          return Container(
            color: Colors.grey.shade200,
            child: const Icon(Icons.person, color: Colors.grey),
          );
        },
      );
    } else {
      imageWidget = Image.asset(
        path,
        fit: BoxFit.cover,
        errorBuilder: (context, error, stackTrace) {
          return Container(
            color: Colors.grey.shade200,
            child: const Icon(Icons.person, color: Colors.grey),
          );
        },
      );
    }

    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(color: Colors.blue, width: 1),
      ),
      child: ClipOval(child: imageWidget),
    );
  }
}
