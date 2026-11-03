import '../models/enums.dart';

class Session {
  final String userId;
  final String email;
  final String fullName;
  final UserRole role;
  final String? phoneNumber;
  final String? municipality;
  final String accessToken;

  const Session({
    required this.userId,
    required this.email,
    required this.fullName,
    required this.role,
    this.phoneNumber,
    this.municipality,
    required this.accessToken,
  });

  Map<String, dynamic> toJson() => {
    'userId': userId,
    'email': email,
    'fullName': fullName,
    'role': role.value,
    'phoneNumber': phoneNumber,
    'municipality': municipality,
    'accessToken': accessToken,
  };

  factory Session.fromJson(Map<String, dynamic> json) => Session(
    userId: json['userId'] as String,
    email: json['email'] as String,
    fullName: json['fullName'] as String,
    role: UserRole.fromValue(json['role'] as String),
    phoneNumber: json['phoneNumber'] as String?,
    municipality: json['municipality'] as String?,
    accessToken: json['accessToken'] as String,
  );
}
