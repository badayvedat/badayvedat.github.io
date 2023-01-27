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
    }).catch((error) => { console.log(error) });
    return response.data.id
}

const updateComment = async (comment_body, comment_id, octokit) => {
    const { context = {} } = github;
    console.log("comment id: " + comment_id)
    response = await octokit.rest.issues.updateComment({
        owner: context.repo.owner,
        repo: context.repo.repo,
        comment_id: comment_id,
        body: getMarkdownSummary(comment_body)
    }).catch((error) => { console.log(error) });
    console.log("update");
    console.log(response);
    return response.data.id
}


const getMarkdownSummary = (body) => {
    const summary_block = "<summary>Show Output</summary>\n"
    const code_ticks = "\n```\n"
    const output = `<details>${summary_block}${code_ticks}${body}${code_ticks}</details>`
    return output
}
 

const logOutputs = ({filename, comment_id, octokit}) => {
    try {
        const data = fs.readFileSync(filename, 'utf8');
        console.log("data")
        console.log(data)
        updateComment(data, comment_id, octokit)
    } catch (err) {
        console.error(err);
    }
}

async function run() {
    try {
        const octokit = github.getOctokit(process.env["GITHUB_TOKEN"]);

        const comment_id = createComment(
            getMarkdownSummary(""), 
            octokit
        );
        cron.schedule('*/30 * * * * *', () => {
            logOutputs({
                filename: "output.txt",
                comment_id: comment_id,
                octokit: octokit,
            });
            console.log('running every 30 seconds');
        });

    } catch (error) {
        core.error(error);
        core.setFailed(error.message);
    }
}

run();
