# Launch checklist

The implementation and examples are local until the release gate is complete. Do not describe the package as released before a public `v0.1.0` tag exists.

Before release: obtain independent review; run CI on Ubuntu and Windows with Python 3.10 and 3.13; verify a fresh environment can install the package and execute clean, violation, invalid-input, and adversarial examples with the documented JSON and exit codes. Review the README's scope limits and confirm examples remain synthetic. After those checks, publish the reviewed `v0.1.0` tag and verify the public release receipt.
