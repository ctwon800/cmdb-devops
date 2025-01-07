import { request } from '@/api/service'

export const crudOptions = (vm) => {
  return {
    pageOptions: {
      compact: true
    },
    options: {
      height: '100%',
      rowId: 'id'
    },
    selectionRow: {
      align: 'center',
      width: 46
    },
    rowHandle: {
      width: 240,
      fixed: 'right',
      view: {
        thin: true,
        text: '',
        disabled () {
          return !vm.hasPermissions('Retrieve')
        }
      },
      edit: {
        thin: true,
        text: '',
        show: false,
        disabled () {
          return !vm.hasPermissions('Update')
        }
      },
      remove: {
        thin: true,
        text: '',
        disabled () {
          return !vm.hasPermissions('Delete')
        }
      },
      custom: [
        {
          thin: true,
          text: '执行结果',
          size: 'small',
          type: 'primary',
          show () {
            return vm.hasPermissions('tasksResults')
          },
          emit: 'tasksResults'
        }
      ]
    },
    viewOptions: {
      componentType: 'form'
    },
    formOptions: {
      defaultSpan: 12 // 默认的表单 span
    },
    indexRow: { // 或者直接传true,不显示title，不居中
      title: '序号',
      align: 'center',
      width: 40
    },
    columns: [
      {
        title: 'ID',
        key: 'id',
        disabled: true,
        form: {
          disabled: true
        }
      },
      {
        title: '任务名',
        key: 'periodic_task_name',
        minWidth: 80,
        search: {
          disabled: false
        },
        dict: {
          data: vm.dictionary('periodic_task_name')
        },
        form: {
          show: false,
          component: {
            span: 12,
            clearable: true
          }
        }
      },
      {
        title: '任务id',
        key: 'task_id',
        minWidth: 145,
        // disabled: true,
        dict: {
          data: vm.dictionary('task_id')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '任务类型',
        key: 'task_name',
        width: 120,
        type: 'radio',
        search: {
          disabled: false
        },
        dict: {
          url: '/api/celery/task/get_task_type/',
          value: 'task_type',
          label: 'task_type'
          // data: vm.dictionary('celery_type_radio')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '执行状态',
        key: 'status',
        width: 80,
        type: 'radio',
        search: {
          disabled: false
        },
        dict: {
          // data: vm.dictionary('status')
          cache: true,
          url: 'api/celery/task_results/get_task_status/',
          value: 'status',
          label: 'status',
          getData: (url, dict, {
            form
          }) => {
            return request({
              url: url
            }).then(ret => {
              return ret.data.data
            })
          }

        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '执行结果',
        key: 'result',
        type: 'text-area',
        disabled: true,
        width: 180,
        dict: {
          data: vm.dictionary('result')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '执行时间',
        key: 'date_done',
        width: 120,
        dict: {
          data: vm.dictionary('date_done')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      }
    ]
  }
}
