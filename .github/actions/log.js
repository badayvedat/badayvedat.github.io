const core = require('@actions/core');
const github = require('@actions/github');


const createComment = async (body) => {
    response = await octokit.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: body
    });
    return response.data.id
}


async function run() {
    try {
        let body = "<details><summary>Show Output</summary>\n\n```\nDetails\n```\n</details>"
        
        const octokit = github.getOctokit(process.env["GITHUB_TOKEN"]);
        const { context = {} } = github;

        const comment_id = createComment();

        console.log(comment_id);
    } catch (error) {
        core.error(error);
        core.setFailed(error.message);
    }
}

run();