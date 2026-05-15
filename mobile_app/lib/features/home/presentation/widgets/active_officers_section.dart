import 'package:flutter/material.dart';

class ActiveOfficersSection extends StatelessWidget {
  const ActiveOfficersSection({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: const [
        Text(
          'Active Officers',
          style: TextStyle(
            fontSize: 22,
            fontWeight: FontWeight.w800,
            color: Colors.black,
          ),
        ),
        SizedBox(height: 18),
        _OfficerCard(
          name: 'Ahmed Mohamed',
          role: 'Runway Safety Officer',
          imagePath: 'assets/images/user_image.jpg',
        ),
        SizedBox(height: 14),
        _OfficerCard(
          name: 'Omar Ali',
          role: 'Inspection Officer',
          imagePath: 'assets/images/user_image.jpg',
        ),
      ],
    );
  }
}

class _OfficerCard extends StatelessWidget {
  final String name;
  final String role;
  final String imagePath;

  const _OfficerCard({
    required this.name,
    required this.role,
    required this.imagePath,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.10),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          CircleAvatar(radius: 24, backgroundImage: AssetImage(imagePath)),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  name,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                    color: Colors.black,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  role,
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w500,
                    color: Colors.black.withOpacity(0.55),
                  ),
                ),
              ],
            ),
          ),
          Container(
            width: 11,
            height: 11,
            decoration: const BoxDecoration(
              color: Color(0xff58F25B),
              shape: BoxShape.circle,
            ),
          ),
        ],
      ),
    );
  }
}
