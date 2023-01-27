const core = require('@actions/core');
const github = require('@actions/github');
const cron = require('node-cron');
const fs = require('fs');


const createComment = async (comment_body, octokit) => {
    const { context = {} } = github;

    response = await octokit.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: comment_body
    });
    return response.data.id
}

const updateComment = async (comment_body, comment_id, octokit) => {
    const { context = {} } = github;

    response = await octokit.rest.issues.updateComment({
        owner: context.repo.owner,
        repo: context.repo.repo,
        comment_id: comment_id,
        body: comment_body
    });
    return response.data.id
}


const logOutputs = (filename, comment_id, octokit) => {
    try {
        const data = fs.readFileSync(filename, 'utf8');
        updateComment(data, comment_id, octokit)
    } catch (err) {
        console.error(err);
    }
}

async function run() {
    try {
        const body = "<details><summary>Show Output</summary>\n\n```\nDetails\n```\n</details>"
        
        const octokit = github.getOctokit(process.env["GITHUB_TOKEN"]);

        const comment_id = createComment(body, octokit);
        cron.schedule('*/10 * * * * *', () => {
            logOutputs("output.txt", comment_id, octokit);
            console.log('running every 30 seconds');
        });

    } catch (error) {
        core.error(error);
        core.setFailed(error.message);
    }
}

run();