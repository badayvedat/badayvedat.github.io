
require('dotenv').config();

const core = require('@actions/core');
const github = require('@actions/github');

let body = "<details><summary>Show Output</summary>```\n\nIntegration test details\n```</details>"

console.log(process.env)

const octokit = github.getOctokit()

const response = octokit.rest.issues.createComment({
    issue_number: context.issue.number,
    owner: context.repo.owner,
    repo: context.repo.repo,
    body: body
});

const comment_id = response.data.id;

console.log(response);
console.log(github.context);
