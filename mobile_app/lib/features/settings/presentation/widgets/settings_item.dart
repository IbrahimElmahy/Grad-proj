import 'package:flutter/material.dart';

class SettingsItem extends StatelessWidget {
  final IconData? icon;
  final String title;
  final String? trailingText;
  final String? smallLeadingText;
  final VoidCallback onTap;

  const SettingsItem({
    super.key,
    required this.title,
    required this.onTap,
    this.icon,
    this.trailingText,
    this.smallLeadingText,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        InkWell(
          borderRadius: BorderRadius.circular(12),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 14),
            child: Row(
              children: [
                if (icon != null) ...[
                  Icon(
                    icon,
                    color: const Color(0xff1D1D1D),
                    size: 28,
                  ),
                  const SizedBox(width: 14),
                ] else if (smallLeadingText != null) ...[
                  SizedBox(
                    width: 34,
                    child: Text(
                      smallLeadingText!,
                      style: const TextStyle(
                        fontSize: 8,
                        color: Colors.black,
                        fontWeight: FontWeight.w400,
                      ),
                    ),
                  ),
                  const SizedBox(width: 6),
                ],
                Expanded(
                  child: Text(
                    title,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w500,
                      color: Colors.black,
                    ),
                  ),
                ),
                if (trailingText != null)
                  Padding(
                    padding: const EdgeInsets.only(right: 12),
                    child: Text(
                      trailingText!,
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w400,
                        color: Colors.black,
                      ),
                    ),
                  ),
                const Icon(
                  Icons.chevron_right,
                  color: Color(0xff062B6F),
                  size: 28,
                ),
              ],
            ),
          ),
        ),
        const Divider(
          height: 1,
          thickness: 1,
          color: Color(0xff7D8CA3),
        ),
      ],
    );
  }
}