import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:gradiuationg_project/core/constants/constants.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/widgets/user_avatar.dart';
import '../../../auth/data/auth_session.dart';
import '../../../auth/data/auth_service.dart';

class AccountInfoScreen extends StatefulWidget {
  const AccountInfoScreen({super.key});

  @override
  State<AccountInfoScreen> createState() => _AccountInfoScreenState();
}

class _AccountInfoScreenState extends State<AccountInfoScreen> {
  bool _isEditing = false;
  bool _isSaving = false;
  late TextEditingController _nameController;

  List<int>? _selectedImageBytes;
  String? _selectedImageName;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: AuthSession.user?.name ?? '');
  }

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  String _getInitials(String name) {
    if (name.trim().isEmpty) return 'US';
    final parts = name.trim().split(RegExp(r'\s+'));
    if (parts.length >= 2) {
      if (parts[0].isNotEmpty && parts[1].isNotEmpty) {
        return (parts[0][0] + parts[1][0]).toUpperCase();
      }
    }
    if (parts.isNotEmpty && parts[0].isNotEmpty) {
      return parts[0][0].toUpperCase();
    }
    return 'US';
  }

  Future<void> _pickImage() async {
    try {
      final result = await FilePicker.pickFiles(
        type: FileType.image,
        withData: true,
      );
      if (result != null && result.files.single.bytes != null) {
        setState(() {
          _selectedImageBytes = result.files.single.bytes;
          _selectedImageName = result.files.single.name;
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to pick image: $e')),
      );
    }
  }

  Future<void> _saveProfile() async {
    final user = AuthSession.user;
    if (user == null) return;

    if (_nameController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Name cannot be empty')),
      );
      return;
    }

    setState(() {
      _isSaving = true;
    });

    try {
      await const AuthService().updateProfile(
        userId: user.id,
        name: _nameController.text.trim(),
        imageBytes: _selectedImageBytes,
        imageName: _selectedImageName,
      );

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Profile updated successfully!')),
      );

      setState(() {
        _isEditing = false;
        _isSaving = false;
        _selectedImageBytes = null;
        _selectedImageName = null;
      });
    } catch (e) {
      setState(() {
        _isSaving = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to update profile: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!AuthSession.isSignedIn) {
      WidgetsBinding.instance?.addPostFrameCallback((_) {
        Navigator.pushReplacementNamed(context, AppRoutes.welcome);
      });
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    final user = AuthSession.user;
    final userName = user?.name ?? 'Safety Officer';
    final userRole = user?.role ?? 'Safety Officer';
    final initials = _getInitials(userName);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.primary,
        elevation: 0,
        leading: _isEditing
            ? IconButton(
                icon: const Icon(Icons.close),
                onPressed: _isSaving
                    ? null
                    : () {
                        setState(() {
                          _isEditing = false;
                          _selectedImageBytes = null;
                          _selectedImageName = null;
                          _nameController.text = user?.name ?? '';
                        });
                      },
              )
            : null,
        title: Text(
          _isEditing ? 'Edit Profile' : 'Account Details',
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 19),
        ),
        actions: [
          if (_isEditing)
            _isSaving
                ? const Center(
                    child: Padding(
                      padding: EdgeInsets.symmetric(horizontal: 16),
                      child: SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          color: Colors.white,
                          strokeWidth: 2,
                        ),
                      ),
                    ),
                  )
                : IconButton(
                    icon: const Icon(Icons.check),
                    onPressed: _saveProfile,
                  )
          else
            IconButton(
              icon: const Icon(Icons.edit),
              onPressed: () {
                setState(() {
                  _isEditing = true;
                  _nameController.text = user?.name ?? '';
                });
              },
            ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Container(
              padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(24),
                border: Border.all(color: AppColors.border.withOpacity(0.5)),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.02),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Column(
                children: [
                  Stack(
                    alignment: Alignment.center,
                    children: [
                      // Avatar Preview
                      if (_selectedImageBytes != null)
                        Container(
                          width: 84,
                          height: 84,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            border: Border.all(color: Colors.blue, width: 1),
                          ),
                          child: ClipOval(
                            child: Image.memory(
                              Uint8List.fromList(_selectedImageBytes!),
                              fit: BoxFit.cover,
                            ),
                          ),
                        )
                      else if (user?.profilePicture != null && user!.profilePicture!.isNotEmpty)
                        UserAvatar(
                          imagePath: user.profilePicture,
                          size: 84,
                        )
                      else
                        Container(
                          width: 84,
                          height: 84,
                          decoration: BoxDecoration(
                            color: AppColors.primary.withOpacity(0.1),
                            shape: BoxShape.circle,
                          ),
                          child: Center(
                            child: Text(
                              initials,
                              style: const TextStyle(
                                fontSize: 28,
                                fontWeight: FontWeight.w900,
                                color: AppColors.primary,
                              ),
                            ),
                          ),
                        ),
                      
                      // Camera overlay if editing
                      if (_isEditing)
                        Positioned(
                          right: 0,
                          bottom: 0,
                          child: Material(
                            color: AppColors.primary,
                            shape: const CircleBorder(),
                            elevation: 4,
                            child: InkWell(
                              onTap: _isSaving ? null : _pickImage,
                              customBorder: const CircleBorder(),
                              child: const Padding(
                                padding: EdgeInsets.all(8.0),
                                child: Icon(
                                  Icons.camera_alt,
                                  size: 16,
                                  color: Colors.white,
                                ),
                              ),
                            ),
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  if (_isEditing)
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 24),
                      child: TextField(
                        controller: _nameController,
                        textAlign: TextAlign.center,
                        enabled: !_isSaving,
                        decoration: const InputDecoration(
                          hintText: 'Enter your name',
                          focusedBorder: UnderlineInputBorder(
                            borderSide: BorderSide(color: AppColors.primary, width: 2),
                          ),
                        ),
                        style: const TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.w900,
                          color: AppColors.textDark,
                          letterSpacing: -0.5,
                        ),
                      ),
                    )
                  else ...[
                    Text(
                      userName,
                      style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.w900,
                        color: AppColors.textDark,
                        letterSpacing: -0.5,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      userRole,
                      style: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textGrey,
                      ),
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Profile Details Card
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(24),
                border: Border.all(color: AppColors.border.withOpacity(0.5)),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.02),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Column(
                children: [
                  _AccountRow(
                    icon: Icons.person_outline_rounded,
                    label: 'Username',
                    value: user?.username ?? '-',
                  ),
                  const Divider(height: 1, color: AppColors.background),
                  _AccountRow(
                    icon: Icons.email_outlined,
                    label: 'Email Address',
                    value: user?.email ?? '-',
                  ),
                  const Divider(height: 1, color: AppColors.background),
                  _AccountRow(
                    icon: Icons.badge_outlined,
                    label: 'System Role',
                    value: user?.role ?? '-',
                  ),
                  const Divider(height: 1, color: AppColors.background),
                  _AccountRow(
                    icon: Icons.local_airport_rounded,
                    label: 'Airport Location',
                    value: user?.airport ?? 'RVMS Operations',
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _AccountRow extends StatelessWidget {
  const _AccountRow({
    required this.icon,
    required this.label,
    required this.value,
  });

  final IconData icon;
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 8),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: AppColors.background,
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: AppColors.primary, size: 22),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textGrey,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  value,
                  style: const TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w800,
                    color: AppColors.textDark,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
