import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import '../config/service_provider_config.dart';

class GoogleSignInButton extends StatelessWidget {
  final bool isLoading;
  final VoidCallback onPressed;
  const GoogleSignInButton({
    super.key,
    required this.isLoading,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 50,
      child: OutlinedButton.icon(
        icon: SvgPicture.network(
          'https://www.gstatic.com/images/branding/product/1x/goog_onboarding_logo_2x_light.svg',
          height: 24,
          width: 24,
          placeholderBuilder: (context) =>
              const SizedBox(height: 24, width: 24),
        ),
        label: isLoading
            ? const SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(strokeWidth: 2),
              )
            : Text(
                'Sign in with ${ServiceProviderConfig.getDisplayName('google')}',
              ),
        onPressed: isLoading ? null : onPressed,
        style: OutlinedButton.styleFrom(
          foregroundColor: Colors.black,
          side: const BorderSide(color: Colors.grey),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
    );
  }
}
