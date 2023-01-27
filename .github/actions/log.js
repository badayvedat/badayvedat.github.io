const core = require('@actions/core');
const github = require('@actions/github');

async function run() {
    try {
        let body = "<details><summary>Show Output</summary>\n\n```\nDetails\n```\n</details>"
        
        const octokit = github.getOctokit(process.env["GITHUB_TOKEN"]);
        const { context = {} } = github;
        
        const response = await octokit.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: body
        });

        const comment_id = response.data.id;

        console.log(response);
        console.log(github.context);
    } catch (error) {
        core.error(error);
        core.setFailed(error.message);
    }
}

run();