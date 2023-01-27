let body = "<details><summary>Show Output</summary>```\n\nIntegration test details\n```</details>"
response = await github.rest.issues.createComment({
    issue_number: context.issue.number,
    owner: context.repo.owner,
    repo: context.repo.repo,
    body: body
});
const comment_id = response.data.id;
console.log(comment_id);
console.log(context);