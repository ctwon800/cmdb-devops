// import { request } from '@/api/service'

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
        show: false,
        text: '',
        disabled () {
          return !vm.hasPermissions('Update')
        }
      },
      remove: {
        thin: true,
        text: '',
        show: false,
        disabled () {
          return !vm.hasPermissions('Delete')
        }
      },
      custom: [
        {
          thin: true,
          text: '录像回放',
          size: 'small',
          type: 'primary',
          icon: 'el-icon-video-camera-solid',
          show () {
            return vm.hasPermissions('recordVideo')
          },
          emit: 'recordVideo'
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
      width: 60
    },
    columns: [
      {
        title: '操作人',
        key: 'record_user',
        width: 145,
        search: {
          disabled: false
        },
        dict: {
          data: vm.dictionary('record_user')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '远程操作服务器名称',
        key: 'record_host',
        width: 145,
        search: {
          disabled: false
        },
        dict: {
          data: vm.dictionary('record_host')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '录像开始时间',
        key: 'record_start_time',
        width: 145,
        dict: {
          data: vm.dictionary('record_start_time')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '录像结束时间',
        key: 'record_end_time',
        width: 145,
        dict: {
          data: vm.dictionary('record_end_time')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '录像文件',
        key: 'record_filepath',
        minWidth: 145,
        dict: {
          data: vm.dictionary('record_filepath')
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
