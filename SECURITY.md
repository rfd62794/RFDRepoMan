# Security Model

RFDRepoMan can push commits, merge branches and pull requests, change repository visibility, and delete remote branches on the operator's behalf. These actions can expose code, alter shared history, or permanently remove references to unmerged work.

The service reduces risk by exposing only named, typed operations; requiring explicit confirmation for consequential actions; and applying a separately authorized policy override when a repository has declared its own quality policy. These controls do not remove the operator's responsibility to understand the repository, target branch, remote account, and consequences of each authorization.

This warning follows the disclosure standard commonly described as the "lethal trifecta": access to sensitive data, access to external systems, and the ability to act on an operator's behalf. RepoMan is intentionally constrained, but authorized operators must treat every confirmed action as consequential.

## Reporting

Do not include credentials in issue reports. Report suspected vulnerabilities privately to the project maintainers with reproduction steps, affected version, and impact.
