const core = require('@actions/core');
const github = require('@actions/github');
const cron = require('node-cron');
const fs = require('fs');


const createComment = async ({
    comment_body,
    octokit
}) => {
    const {
        context = {}
    } = github;

    response = await octokit.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: comment_body
    }).catch((error) => {
        console.error(error)
    });
    return response.data.id
}

const updateComment = async ({
    comment_body,
    comment_id,
    octokit
}) => {
    const {
        context = {}
    } = github;
    console.log("start octokit update")
    response = await octokit.rest.issues.updateComment({
        owner: context.repo.owner,
        repo: context.repo.repo,
        comment_id: comment_id,
        body: getMarkdownSummary(comment_body)
    }).catch((error) => {
        console.error(error)
    });
    console.log("end octokit update")
    await response;
    console.log("update response: " + response);
    return response.data.id
}


const getMarkdownSummary = (body) => {
    const summary_block = "<summary>Show Output</summary>\n"
    const code_ticks = "\n```\n"
    const output = `<details>${summary_block}${code_ticks}${body}${code_ticks}</details>`
    return output
}

const getLogFilePath = () => "output.log"
const getProcessSuccessFilePath = () => "SUCCESS"

const logOutputs = async ({
    comment_id,
    octokit
}) => {
    console.log("log outputs");
    const log_path = getLogFilePath();

    try {
        const data = fs.readFileSync(log_path, 'utf8');
        console.log("Start update: " + new Date())
        await updateComment({
            comment_body: data,
            comment_id: comment_id,
            octokit: octokit
        });
        console.log("End update: " + new Date())
    } catch (err) {
        console.error(err);
    }
}

const checkOutput = ({
    comment_id,
    octokit
}) => {
    console.log("start interval: " + new Date())
    logOutputs({
        comment_id: comment_id,
        octokit: octokit,
    });
    if (isProcessFinished()) {
        console.log("process finished")
        logOutputs({
            comment_id: comment_id,
            octokit: octokit,
        });
        process.exit(0);
    }
    console.log("end interval");
}

const isProcessFinished = () => fs.existsSync(
    getProcessSuccessFilePath()
);

async function run() {
    try {
        const octokit = github.getOctokit(process.env["GITHUB_TOKEN"]);

        const comment_id = await createComment({
            comment_body: getMarkdownSummary("Waiting for command logs.."),
            octokit: octokit
        });

        const check_interval = 30 * 1000;
        setInterval(checkOutput, check_interval, {
            comment_id: comment_id,
            octokit: octokit
        });

    } catch (error) {
        core.error(error);
        core.setFailed(error.message);
    }
}

run();